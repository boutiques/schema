#!/usr/bin/env python

import simplejson
import tempfile
import argparse
import sys
import os.path as op
from jsonschema import validate, ValidationError
from argparse import ArgumentParser
from boutiques import __file__ as bfile


# An exception class specific to creating descriptors.
class CreatorError(ValidationError):
    pass


class CreateDescriptor(object):
    def __init__(self, parser=None, **kwargs):
        self.descriptor = {
            "command-line": "echo [PARAM1] [PARAM2] [FLAG1] > [OUTPUT1]",
            "container-image": {
                "image": kwargs.get("container") or "user/image",
                "type": kwargs.get("container-type") or "singularity",
                "index": kwargs.get("container-index") or "docker://"
            },
            "description": kwargs.get("description") or "tool description",
            "error-codes": [
                {
                    "code": kwargs.get("error-code") or 1,
                    "description": kwargs.get("error-message") or "Crashed"
                }
            ],
            "groups": [
                {
                    "all-or-none": True,
                    "mutually-exclusive": False,
                    "one-is-required": False,
                    "id": "group1",
                    "members": [
                        "param1",
                        "flag1"
                    ],
                    "name": "the param group"
                }
            ],
            "inputs": [
                {
                    "id": "param1",
                    "name": "The first parameter",
                    "optional": True,
                    "type": "File",
                    "value-key": "[PARAM1]"
                },
                {
                    "id": "param2",
                    "name": "The second parameter",
                    "optional": False,
                    "type": "String",
                    "value-choices": [
                        "mychoice1.log",
                        "mychoice2.log"
                    ],
                    "value-key": "[PARAM2]"
                },
                {
                    "command-line-flag": "-f",
                    "id": "flag1",
                    "name": "The first flag",
                    "optional": True,
                    "type": "Flag",
                    "value-key": "[FLAG1]"
                }
            ],
            "name": kwargs.get("name") or "tool name",
            "output-files": [
                {
                    "id": "output1",
                    "name": "The first output",
                    "optional": False,
                    "value-key": "[OUTPUT1]",
                    "path-template": "[PARAM2].txt",
                    "path-template-stripped-extensions": [
                        ".log"
                    ]
                }
            ],
            "schema-version": "0.5",
            "suggested-resources": {
                "cpu-cores": 1,
                "ram": 1,
                "walltime-estimate": 60
            },
            "tags": {
                "purpose": "testing",
                "foo": "bar",
                "status": "example"
            },
            "tool-version": "v0.1.0"
        }

        self.count = 0
        if parser is None:
            return self.descriptor
        else:
            self.parser = parser
            if type(parser) is not argparse.ArgumentParser:
                raise CreatorError(msg="Invalid argument parser")

            self.parseParser(**kwargs)

    def counter(self):
        self.count += 1
        return self.count

    def parseParser(self, **kwargs):
        self.descriptor["command-line"] = kwargs.get("execname")
        for act in self.parser._actions:
            delta = self.parseAction(act)
        print(self.descriptor["command-line"])

    def parseAction(self, action, **kwargs):
        if type(action) is argparse._HelpAction:
            if kwargs.get("verbose"):
                print("(skipping _HelpAction)")
            return {}

        elif (type(action) is argparse._SubParsersAction and
              not kwargs.get("addParser")):
            if kwargs.get("verbose"):
                print("(interpreting _SubParsersAction)")
            # print("subbyyyyy")
            subparser = self.parseAction(action, addParser=True)
            inpts = {}
            for act in action.choices:
                inpts[act] = {}
                for subact in action.choices[act]._actions:
                    # input relies on sub action selection
                    inpts[act].update(self.parseAction(subact, subparser=act))
                # act enables all the subacts in delta
                # "value-disables": {
                #     "mychoice1.log": [],
                #     "mychoice2.log": []
            # Set "value-disables" based on overlap
            self.descriptor["inputs"] += [subparser]
            # acts in bigdelta are mutually exclusive
            return subparser.update(inpts)
        else:
            actdict = vars(action)
            if action.dest == "==SUPPRESS==":
                adest = "subparser-{0}".format(self.counter())
            else:
                adest = action.dest

            print(action)
            newinput = {
                "id": adest,
                "name": adest,
                "description": action.help,
                "optional": not action.required,
                "type": action.type or "String",
                "value-key": "{0}".format(adest.upper())
            }
            if action.default:
                newinput["default-value"] = action.default
            if action.choices:
                newinput["value-choices"] = action.choices
            if len(action.option_strings):
                newinput["command-line-flag"] = action.option_strings[0]
            if type(action) is argparse._StoreTrueAction: 
                newinput["type"] = "Flag"

            if any(newinput["id"] == it["id"]
                   for it in self.descriptor["inputs"]):
                print("duplicate; rename or ignore, ID won't be added twice")
            else:
                self.descriptor["command-line"] += " {0}".format(adest.upper())
                self.descriptor["inputs"] += [newinput]
            return newinput

