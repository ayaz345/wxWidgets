"""
C bindings generator
Author: Luke A. Guest
"""

import os

from common import *

class CBuilder:
    def __init__(self, doxyparse, outputdir):
        self.doxyparser = doxyparse
        self.output_dir = outputdir

    def make_bindings(self):
        output_dir = os.path.abspath(os.path.join(self.output_dir, "c"))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for aclass in self.doxyparser.classes:
            # This bit doesn't work, because the aclass.name is not the same as
            # those listed in common
            if aclass.name in excluded_classes:
                #print "Skipping %s" % aclass.name
                continue

            self.make_c_header(output_dir, aclass)


    def make_c_header(self, output_dir, aclass):
        filename = os.path.join(output_dir, f"{aclass.name[2:].lower()}.hh")
        enums_text = make_enums(aclass)
        method_text = self.make_c_methods(aclass)
        class_name = aclass.name[2:].capitalize()
        text = """
// Enums
%s

%s
""" % (enums_text, method_text)

        with open(filename, "wb") as afile:
            afile.write(text)


    def make_c_methods(self, aclass):
        wxc_classname = f'wxC{aclass.name[2:].capitalize()}'

        retval = "".join(
            """
// %s
%s%s;\n\n
"""
            % (
                amethod.brief_description,
                f'{wxc_classname}* {wxc_classname}_{amethod.name}',
                amethod.argsstring,
            )
            for amethod in aclass.constructors
        )
        for amethod in aclass.methods:
            if amethod.name.startswith('m_'):
                # for some reason, public members are listed as methods
                continue

            args = f'({wxc_classname}* obj'
            if amethod.argsstring.find('()') != -1:
                args += ')'
            else:
                args += f', {amethod.argsstring[1:].strip()}'

            retval += """
// %s
%s %s%s;\n
""" % (
                amethod.detailed_description,
                amethod.return_type,
                f'{wxc_classname}_{amethod.name}',
                args,
            )

        return retval
