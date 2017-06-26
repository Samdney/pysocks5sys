#!/usr/bin/env python3

#_____________________________________________________________________________
#
# filter for changing the gender of pronouns in a plaintext
#
# Author:   Samdney  <contact@carolin-zoebelein.de>   D4A7 35E8 D47F 801F 2CF6 2BA7 927A FD3C DE47 E13B 
# License:  See LICENSE for licensing information
#_____________________________________________________________________________
"""
***
GENDER SWITCHING
***
Switching pronouns in a plaintext message of one gender, to the pronouns of the other gender.

---
The problems of gender switching
---
Assumptions:
1. The message is in English => English pronouns
	This are: he, she, him, her, his, hers (6 single pronouns)
2. We can have two possible cases:
	=> A random pattern (or something written by a person with terrible writing skills ;)
	=> A natural language text with established English grammar

3. We have the following possible pronoun pairs:
	he 	<=> she		Personal pronoun - subject
	him <=> her		Personal pronoun - object
	his <=> her		Possessive determine
	his <=> hers	Possessive pronoun
	(4 pairs)

	Problem:	This map is NOT injective!
	Because:	her -> him or his
				his -> her or hers
	=> We have to find an additional helpful quality!
	
	First idea:	We look for the position within a sentence.
	Problem: An pronoun can be direct or indirect
	=> Idea not helpful
	
	Second idea: Looking for a natural language parser which can
	tell me which kind of word it is (SUB=subject, OBJ=object, etc., ...)
	
	=> Solution is only so good like the natural language parser!
	=> I found this wrapper parser: https://github.com/EducationalTestingService/python-zpar				
"""

import string
import sys

class gender_filter():

	def __init__(self):
		self.msg_new	= " "

	def change_msg(self,filter_switch,msg):
		switch = gender_filter()
		if filter_switch == 0:
			_msg_new = msg
		elif filter_switch == 1:
			_msg_new = switch.simple_switch(msg)
		else:
			_msg_new = switch.lingu_switch(msg)

		self.msg_new = _msg_new

	# Switch one pronoun pair 
	def switch_one_pronoun_pair(self,pn1,pn2,msg):
		tmp = "6m7Q6q16"							# Placeholder should be no "real" word, something with lim -> 0 probability to appear in msg

		msg1 	= msg.replace(pn1,tmp)
		msg2 	= msg1.replace(pn2,pn1)
		msg3	= msg2.replace(tmp,pn2)

		msg_switched = msg3
		return msg_switched

	# Switch for all possible positions within a sentence and msg
	def switch_one_pronoun_pair_allpos(self,pn1,pn2,msg):
		myfilter = gender_filter()
		_msg_new = msg
		# Beginning and Middle
		_msg_new = myfilter.switch_one_pronoun_pair(" " + str(pn1) + " ", " " + str(pn2) + " ",_msg_new)
		_msg_new = myfilter.switch_one_pronoun_pair(" " + str(pn1) + ", ", " " + str(pn2) + ", ",_msg_new)
		
		# End
		_msg_new = myfilter.switch_one_pronoun_pair(" " + str(pn1) + ".", " " + str(pn2) + ".",_msg_new)
		_msg_new = myfilter.switch_one_pronoun_pair(" " + str(pn1) + "!", " " + str(pn2) + "!",_msg_new)
		_msg_new = myfilter.switch_one_pronoun_pair(" " + str(pn1) + "?", " " + str(pn2) + "?",_msg_new)
		return _msg_new
		

	"""
	# SIMPLE_SWITCH
	"""	
	# Idea: Simple find and replace.
	#	Step1:	Switch he <=> she
	#	Step2:	Switch him <=> her
	#	Step3:	Switch his <=> her
	#	Step4:	Switch his <=> hers
	# Comment: The pronoun parsing only works correct for an msg which follows the established rules of English grammar. Absolutely not, for a random pattern text
	# Comment: The input msg variable should contain the full message, at one. If we do parsing for each single data of buffer_size, parsing will not work if
	# 	a pronoun is splited between two buffer packages. E.g.: package1|package2 = msg = "He and sh"|"e are good friends."
	# => Has to be fixed.
	# TODO: Result would be better, if we do switching not chronologically (step1, step2, step3, step4). Instead we should have an additional look at probability
	#	tables for the probability of the appereance of a single pronoun in an English text. Then do the switching of the not-injective pronoun pairs under
	#	consideration of this probabilities.
	def simple_switch(self,msg):
		
		_msg_new = " "
		myfilter = gender_filter()
	
		# Add an additional space character at the beginng of msg
		# Reason: Then you can clearly identify pronouns at the beginning of msg
		_msg_new = " " + str(msg)
	
		# Find and replace for different pronoun pairs
		# Find and replace for different notations: he, He, HE ...
		# Find and replace for different positions within a sentence
		#pronoun_pairs = {"he" : "she", "him":"her", "his":"her", "his":"hers"}
		pronoun_pairs = {"he" : "she", "him":"her", "his":"hers", "his":"her"} # Switching of Step3 with Step4
		
		# Example of the different results
		# Old: He, and SHE likes me so much. HELP him! His dog likes tea and eats with him cake. That's hers.
		# New: She, and HE likes me so much. HELP her! Hers dog likes tea and eats with her cake. That's his.

		# Old: He, and SHE likes me so much. HELP him! His dog likes tea and eats with him cake. That's hers.
		# New: She, and HE likes me so much. HELP his! Her dog likes tea and eats with his cake. That's hers.

        # TODO  If we have very long messages, we should add 'if cases' within the
        # loop, to not always run all 'find and replace' functions for each
        # pronoun pair. E.g. 'he' or 'she' aren't at the end of a senctence, if
        # the sentence follows english grammar rules, or? -> Saving of
        # computation time
		for male in pronoun_pairs:
			pn1 = male
			pn2 = pronoun_pairs[male]
	
			# Lower
			pn1_lower = pn1.lower()
			pn2_lower = pn2.lower()
			_msg_new = myfilter.switch_one_pronoun_pair_allpos(pn1_lower,pn2_lower,_msg_new)

			# Upper
			pn1_upper = pn1.upper()
			pn2_upper = pn2.upper()
			_msg_new = myfilter.switch_one_pronoun_pair_allpos(pn1_upper,pn2_upper,_msg_new)
		
			# Titled
			pn1_titled = pn1.title()
			pn2_titled = pn2.title()
			_msg_new = myfilter.switch_one_pronoun_pair_allpos(pn1_titled,pn2_titled,_msg_new)
				
		# Remove the additional space character from the beginng of msg
		len_msg = len(_msg_new)
		_msg_new = _msg_new[1:len_msg]

		self.msg_new = _msg_new
		return _msg_new

	"""
	# LINGU_SWITCH
	"""	
	# TODO: Not implemented until now
	# Idea: 
	# - Send msg to natural language parser to determine the kind of word (subject, object, ...).
	# - Search for all her and his and their result of the natural language parsing
	# - Use this information to decide if we have: her => him or her => his, his => her or his => hers
	# - Change pronouns under consideration of this additional information
	def lingu_switch(self,msg):
		_msg_new = " "
		self.msg_new = _msg_new
		return _msg_new

"""
# TEST
"""

def test():
	# Test messages
	#msg = "She, you and me. Sheer is funny! He is it, too."
	msg = "He, and SHE likes me so much. HELP him! His dog likes tea and eats with him cake. That's hers."
	print("Old: " + msg)
	
	myfilter = gender_filter()
	myfilter.change_msg(1,msg)
	msg_new = myfilter.msg_new
	print("New: " + msg_new)

if __name__=='__main__':
	test()
