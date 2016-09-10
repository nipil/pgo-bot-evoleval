#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pgo-evoleval
Copyright (c) 2016 nipil <https://github.com/nipil>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: nipil <https://github.com/nipil>
"""

import os
import sys
import json
import codecs
import hashlib
import argparse


from operator import itemgetter, attrgetter, methodcaller


class Pokemon():


	def __init__(self, data):
		self.id = data[u"pokemon_id"]
		try:
			self.iv_a = data[u"individual_attack"] + 0
		except KeyError:
			self.iv_a = 0
		try:
			self.iv_d = data[u"individual_defense"] + 0
		except KeyError:
			self.iv_d = 0
		try:
			self.iv_s = data[u"individual_stamina"] + 0
		except KeyError:
			self.iv_s = 0
		self.iv_p = float(self.iv_a + self.iv_d + self.iv_s) / 45.0
		self.cur_cp = data[u"cp"]


	def __str__(self):
		return "#{0} A({1})+D({2})+S({3})=P({4}) CP({5})".format(self.id, self.iv_a, self.iv_d, self.iv_s, self.iv_p, self.cur_cp)



class Evoleval():


	@staticmethod
	def load_json(path):
		with open(path) as json_data:
			d = json.load(json_data)
		return d


	def __init__(self, inventory_file, locale):
		# init datastores
		self.pokemon_bag = {}
		self.names = {}
		self.families = {}
		self.evolutions = {}
		self.candies = {}
		self.planning = {}
		self.actions = {}
		self.locale = locale
		# paths
		self.sp_inv = os.path.normpath(os.path.expandvars(os.path.expanduser(inventory_file)))
		self.sp_ref = os.path.normpath(os.path.join(os.path.dirname(self.sp_inv), '../data/pokemon.json'))
		if self.locale is None:
			self.sp_loc = None
		else:
			self.sp_loc = os.path.normpath(os.path.join(os.path.dirname(self.sp_inv), '../data/locales/{0}.json'.format(locale)))


	def add_candy(self, data):
		family_id = int(data[u'family_id'])
		family_candy = int(data[u'candy'])
		self.candies[family_id] = family_candy


	def add_pokemon(self, poke):
		if poke.id not in self.pokemon_bag:
			self.pokemon_bag[poke.id] = []
		self.pokemon_bag[poke.id].append(poke)


	def get_pokemon_count(self, p_id):
		try:
			return len(self.pokemon_bag[p_id])
		except KeyError:
			return 0


	def get_family_candies(self, f_id):
		try:
			return self.candies[f_id]
		except KeyError:
			return 0


	def get_evolution_requirement(self, p_id):
		try:
			return self.evolutions[p_id]["next_req"]
		except KeyError:
			return 0

	def load_locale(self):
		if self.sp_loc is None:
			self.locale = {}
		else:
			self.locale = self.load_json(self.sp_loc)


	def localize(self, value):
		if self.locale is None:
			return value
		if value not in self.locale:
			return value
		return self.locale[value]


	def load_reference(self):
		# load reference data
		ref = self.load_json(self.sp_ref)
		for poke in ref:
			info = {}
			p_id = int(poke[u"Number"])
			name = self.localize(poke[u'Name'])
			# ensure that localization is defined
			self.locale[name] = name
			self.locale[p_id] = name
			# family links
			if u"Next Evolution Requirements" in poke:
				# store evolution
				info["family"] = poke[u"Next Evolution Requirements"][u"Family"]
				info["next_req"] = poke[u"Next Evolution Requirements"][u"Amount"]
				info["next_id"] = int(poke[u"Next evolution(s)"][0][u"Number"])
				# add to family
				if info["family"] not in self.families:
					self.families[info["family"]] = []
				self.families[info["family"]].append(p_id)
			else:
				if u"Previous evolution(s)" in poke:
					prev_id = int(poke[u"Previous evolution(s)"][0][u"Number"])
					info["family"] = self.evolutions[prev_id]["family"]
					self.families[info["family"]].append(p_id)
			# store
			self.evolutions[p_id] = info
		# sort families
		for i in sorted(self.families.keys()):
			self.families[i] = sorted(self.families[i])


	def load_inventory(self):
		# load inventory items
		inv = self.load_json(self.sp_inv)
		for k in inv:
			for iid_t, inv_item_data in k.items():
				for iid_st, data in inv_item_data.items():
					if iid_st == "candy":
						self.add_candy(data)
					if iid_st == "pokemon_data":
						if u"is_egg" in data and data[u"is_egg"]:
							continue
						poke = Pokemon(data)
						self.add_pokemon(poke)
		# sort pokemons according to perfection
		for id, pokes in self.pokemon_bag.items():
			self.pokemon_bag[id] = sorted(pokes, key=attrgetter('iv_p', 'cur_cp'), reverse=True)


	def plan_evolution(self):

		for f_id in sorted(self.families.keys()):

			# setup
			candies = self.get_family_candies(f_id)
			p_id_base = self.families[f_id][0]
			pokes = self.get_pokemon_count(p_id_base)
			req = self.get_evolution_requirement(p_id_base)

			# evolve/transfer loop
			transfered = 0
			evolve = 0
			while True:
				# print "candies", candies, "pokes", pokes, "total", candies + pokes, "req", req, "evolve", evolve, "transfered", transfered
				if candies >= req and pokes >= 1:
					# print "evolve"
					candies -= req
					pokes -= 1
					evolve += 1
				elif candies < req and pokes > 1:
					transfer = min(pokes - 1, req - candies)
					# print "transfer", transfer
					candies += transfer
					pokes -= transfer
					transfered += transfer
				else:
					# print "nothing more to do"
					break

			# store action
			self.actions[f_id] = {
				"pid": p_id_base,
				"possible": evolve,
				"missing": candies // req,
				"transfer": transfered,
			}


	def print_pokemons(self):
		print "\n== Pokemon details\n"
		for p_id in sorted(self.pokemon_bag.keys()):
			pokes = self.pokemon_bag[p_id]
			print u"* {0}".format(self.localize(p_id))
			for poke in pokes:
				print "** ({3:.2f}) A/D/S={0}/{1}/{2} CP={4}".format(
					poke.iv_a, poke.iv_d, poke.iv_s, poke.iv_p, poke.cur_cp)


	def print_actions(self):
		print "\n== Evolution actions\n"

		n = sum([ action["possible"] for i, action in self.actions.items() ])
		dt = 26
		t = n * dt
		e = float(t / 1800.0)
		print "{0} evolutions available, {1} seconds per, {2} seconds total, use {3:.2f} eggs".format(n, dt, t, e)

		print "\n|==="
		print "|Pokemon|Transfer|Evolve|Missing"
		for f_id in sorted(self.actions.keys()):
			action = self.actions[f_id]
			p_id = action["pid"]
			try:
				pokes = self.pokemon_bag[p_id]
			except KeyError:
				pass
			print ""

			# display pokemon amount, name and candies
			print u"a|{0} {1} (#{2})\n".format(
				self.get_pokemon_count(action["pid"]),
				self.localize(action["pid"]),
				action["pid"])
			print "{0} candies".format(self.get_family_candies(f_id))

			# display transfer summary and details
			print "a|{0} transfer".format(action["transfer"])
			if action["transfer"] > 0:
				print ""
				for poke in pokes[-action["transfer"]:]:
					print "* ({0:.2f}) CP={1}".format(poke.iv_p, poke.cur_cp)
				print ""

			# display evolution summary and details
			print "a|{0} evolution\n".format(action["possible"])
			if action["possible"] > 0:
				print ""
				for poke in pokes[:action["possible"]]:
					print "* ({0:.2f}) CP={1}".format(poke.iv_p, poke.cur_cp)
				print ""

			# notify of missing pokemons
			print "|{0} missing".format(action["missing"])
		print "|==="


	def get_inv_hash(self, hasher=hashlib.sha256(), blocksize=65536):
		with open(p_inv, 'rb') as inv_file:
			buf = inv_file.read(blocksize)
			while len(buf) > 0:
				hasher.update(buf)
				buf = inv_file.read(blocksize)
			return hasher.hexdigest()

	def output_report(self):
		# compute hash of input file
		inv_hash = self.get_inv_hash()

		# build target file name
		base = os.path.splitext(os.path.split(self.sp_inv)[1])[0]
		target = "{0}_{1}.adoc".format(base, inv_hash)

		# display progress
		print "Generating report {0}".format(target)

		# redirect stdout to file
		stdout_backup = sys.stdout
		sys.stdout = codecs.open(target, 'w', 'utf-8')

		# actual output
		print "= Evoleval report for {0}".format(base)
		self.print_actions()
		self.print_pokemons()

		# restore default stdout
		sys.stdout = stdout_backup


	def run(self):
		self.load_locale()
		self.load_reference()
		self.load_inventory()
		self.plan_evolution()
		self.output_report()


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Evaluate PokemonGo evolutions and inventory')
	parser.add_argument(
		'pgob_dir',
		help='PokemonGo-bot install directory')
	parser.add_argument(
		'--locale',
		action='store',
		default=None,
		choices=['de','fr','ja','pt_br','ru','zh_cn','zh_hk','zh_tw'],
		help='select language other than ENGLISH for pokemon names')
	args = parser.parse_args()

	pgob_web = os.path.join(os.path.normpath(os.path.expandvars(os.path.expanduser(args.pgob_dir))), "web")

	for file in os.listdir(pgob_web):
		p = os.path.splitext(file)
		if p[1] == '.json' and p[0].startswith('inventory-'):
			p_inv = os.path.join(pgob_web, file)
			ee = Evoleval(p_inv, args.locale)
			ee.run()

	print "Now convert the ascidoctor reports (*.adoc) to HTML using the following command: asciidoctor *.adoc"

	sys.exit(0)
