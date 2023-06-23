#!/usr/bin/env python

# Run this script from top-level wxWidgets directory to update the contents of
# include/wx/intl.h and src/common/intl.cpp using information from langtabl.txt
#
# Warning: error detection and reporting here is rudimentary, check if the
# files were updated correctly with "git diff" before committing them!

import os
import string
import sys

def ReadScriptTable():
    scripttable = []
    try:
        f = open('misc/languages/scripttabl.txt')
    except:
        print("Did you run the script from top-level wxWidgets directory?")
        raise

    for i in f:
        ispl = i.split()
        scripttable.append((ispl[0], ispl[1]))
    f.close()
    return scripttable

def ReadSynonymTable():
    synonymtable = []
    try:
        f = open('misc/languages/synonymtabl.txt')
    except:
        print("Did you run the script from top-level wxWidgets directory?")
        raise

    for i in f:
        ispl = i.split()
        synonymtable.append((ispl[0], ispl[1], ispl[2], ispl[3]))
    f.close()
    return synonymtable

def ReadTable():
    table = []
    try:
        f = open('misc/languages/langtabl.txt')
    except:
        print("Did you run the script from top-level wxWidgets directory?")
        raise

    for i in f:
        ispl = i.split()
        table.append((ispl[0], ispl[1], ispl[2], ispl[3], ispl[4], ispl[5], ispl[6], ispl[7], ' '.join(ispl[8:])))
    f.close()
    return table


# Kind may be "include" or "interface".
def WriteEnum(f, table, synonymtable, scripttable, kind = 'include'):
    f.write("""
enum wxLanguage
{
    /// User's default/preferred language as got from OS.
    wxLANGUAGE_DEFAULT,

    /// Unknown language, returned if wxLocale::GetSystemLanguage fails.
    wxLANGUAGE_UNKNOWN,

""");
    knownLangs = []
    output = ''
    for i in table:
        lang = i[0]
        wxver = i[1]
        if lang not in knownLangs:
            output += f'    {lang},'
            if kind == 'interface' and wxver != '-':
                output += '%s///< @since_wx{%s}' % (' ' * (56 - len(lang)), wxver)
            output += '\n'
            knownLangs.append(lang)
    output += """
    /// For custom, user-defined languages.
    wxLANGUAGE_USER_DEFINED,
"""

    if kind == 'include':
       output += '\n    /// Synonyms.'

    output += '\n'

    for i in synonymtable:
        lang = i[0]
        synonym = i[1]
        wxver = i[3]
        output += f'    {lang}'
        if kind == 'include':
           output += ' = %s,\n' % synonym
        elif kind == 'interface':
           if wxver != '-':
             output += ',%s///< Synonym for %s. @since_wx{%s}\n' % (' ' * (42 - len(lang)), synonym, wxver)
           else:
             output += ',%s///< Synonym for %s.\n' % (' ' * (42 - len(lang)), synonym)
        else:
          print("Unknown kind of generated enum")
          raise

    output += '};\n\n'
    f.write(output)

def WriteTable(f, table, synonymtable, scripttable):
    sctable = ''
    for i in scripttable:
        scname = f'"{i[0]}"'
        scalias = f'"{i[1]}"'
        sctable += '    { %s, %s },\n' % (scname, scalias)

    lngtable = ''

    for i in table:
        ibcp47 = f'"{i[2]}"'
        ican = f'"{i[3]}"'
        if ican == '"-"': ican = '""'
        icanbase = f'"{i[4]}"'
        if icanbase == '"-"': icanbase = '""'
        ilang = i[5]
        if ilang == '-': ilang = '0'
        isublang = i[6]
        if isublang == '-': isublang = '0'
        if (i[7] == "LTR") :
            ilayout = "wxLayout_LeftToRight"
        elif (i[7] == "RTL"):
            ilayout = "wxLayout_RightToLeft"
        else:
            print("ERROR: Invalid value for the layout direction")
        lngtable += (
            '    { %-60s %-17s, %-28s, %-15s, %-4s, %-4s, %s, %s },\n'
            % (
                f'{i[0]},',
                ibcp47,
                ican,
                icanbase,
                ilang,
                isublang,
                ilayout,
                i[8],
            )
        )

    f.write("""
// The following data tables are generated by misc/languages/genlang.py
// When making changes, please put them into misc/languages/langtabl.txt

#if !defined(__WIN32__)

#define SETWINLANG(info,lang,sublang)

#else

#define SETWINLANG(info,lang,sublang) \\
    info.WinLang = tabLangData[j].lang; \\
    info.WinSublang = tabLangData[j].sublang;

#endif // __WIN32__

// Data table for known languages
static const struct langData_t
{
    int   wxlang;
    const char* bcp47tag;
    const char* canonical;
    const char* canonicalref;
    wxUint32 winlang;
    wxUint32 winsublang;
    wxLayoutDirection layout;
    const char* desc;
    const char* descnative;
}
tabLangData[] =
{
%s
    { 0, nullptr, nullptr, nullptr, 0, 0, wxLayout_Default, nullptr, nullptr }
};

// Data table for known language scripts
static const struct scriptData_t
{
    const char* scname;
    const char* scalias;
}
tabScriptData[] =
{
%s
    { nullptr, nullptr }
};

void wxUILocale::InitLanguagesDB()
{
    wxLanguageInfo info;
    int j;

    // Known languages
    for (j = 0; tabLangData[j].wxlang != 0; ++j)
    {
      info.Language = tabLangData[j].wxlang;
      info.LocaleTag = tabLangData[j].bcp47tag;
      info.CanonicalName = tabLangData[j].canonical;
      info.CanonicalRef = tabLangData[j].canonicalref;
      info.LayoutDirection = tabLangData[j].layout;
      info.Description = wxString::FromUTF8(tabLangData[j].desc);
      info.DescriptionNative = wxString::FromUTF8(tabLangData[j].descnative);
      SETWINLANG(info, winlang, winsublang)
      AddLanguage(info);
    }

    // Known language scripts
    for (j = 0; tabScriptData[j].scname; ++j)
    {
      gs_scmap_name2alias[tabScriptData[j].scname] = tabScriptData[j].scalias;
      gs_scmap_alias2name[tabScriptData[j].scalias] = tabScriptData[j].scname;
    }
}

""" % (lngtable,sctable))


def ReplaceGeneratedPartOfFile(fname, func):
    """
        Replaces the part of file marked with the special comments with the
        output of func.

        fname is the name of the input file and func must be a function taking
        a file and language table on input and writing the appropriate chunk to
        this file, e.g. WriteEnum or WriteTable.
    """
    with open(fname, 'rt') as fin:
        fnameNew = f'{fname}.new'
        with open(fnameNew, 'wt') as fout:
            betweenBeginAndEnd = 0
            afterEnd = 0
            for l in fin:
                if l == '// --- --- --- generated code begins here --- --- ---\n':
                    if betweenBeginAndEnd or afterEnd:
                        print('Unexpected starting comment.')
                    betweenBeginAndEnd = 1
                    fout.write(l)
                    func(fout, table, synonymtable, scripttable)
                elif l == '// --- --- --- generated code ends here --- --- ---\n':
                    if not betweenBeginAndEnd:
                        print('End comment found before the starting one?')
                        break

                    betweenBeginAndEnd = 0
                    afterEnd = 1

                if not betweenBeginAndEnd:
                    fout.write(l)

            if not afterEnd:
                print(f'Failed to process {fname}.')
                os.remove(fnameNew)
                sys.exit(1)

    os.remove(fname)
    os.rename(fnameNew, fname)

table = ReadTable()
scripttable = ReadScriptTable()
synonymtable = ReadSynonymTable()
ReplaceGeneratedPartOfFile('include/wx/language.h', WriteEnum)
ReplaceGeneratedPartOfFile('interface/wx/language.h', lambda f, table, synonymtable, scripttable: WriteEnum(f, table, synonymtable, scripttable, 'interface'))
ReplaceGeneratedPartOfFile('src/common/languageinfo.cpp', WriteTable)
