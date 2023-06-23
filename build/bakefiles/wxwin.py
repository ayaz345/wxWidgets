#
# Helper functions for wxWidgets bakefiles
#
#


import utils

# We use 'CFG' option in places where bakefile doesn't like it, so we must
# register a substitution function for it that provides additional knowledge
# about the option (in this case that it does not contain dir separators and
# so utils.nativePaths() doesn't have to do anything with it):

try:
    # this fails in 0.1.4 and 0.1.5 has different subst.callbacks signature:
    utils.checkBakefileVersion('0.1.5') 
    def __noopSubst(name, func, caller):
        return f'$({name})'
except AttributeError:
    def __noopSubst(func, name):
        return f'$({name})'
utils.addSubstituteCallback('CFG', __noopSubst)
utils.addSubstituteCallback('LIBDIRNAME', __noopSubst)
utils.addSubstituteCallback('SETUPHDIR', __noopSubst)
utils.addSubstituteCallback('OBJS', __noopSubst)


def mk_wxid(id):
    """Creates wxWidgets library identifier from bakefile target ID that
       follows this convention: DLLs end with 'dll', static libraries
       end with 'lib'. If withPrefix=1, then _wxid is returned instead
       of wxid."""
    return id[:-3] if id.endswith('dll') or id.endswith('lib') else id


# All libs that are part of the main library:
MAIN_LIBS = ['mono', 'base', 'core', 'adv', 'html', 'xml', 'net', 'webview',
             'media', 'qa', 'xrc', 'aui', 'ribbon', 'propgrid', 'richtext', 'stc']
# List of library names/ids for categories with different names:
LIBS_NOGUI = ['xml', 'net']
LIBS_GUI   = ['core', 'adv', 'html', 'gl', 'qa', 'xrc', 'media',
              'aui', 'propgrid', 'richtext', 'stc', 'ribbon', 'webview']
# Additional libraries that must be linked in:
EXTRALIBS = {
    'gl' : '$(EXTRALIBS_OPENGL)',
    'xml' : '$(EXTRALIBS_XML)',
    'html' : '$(EXTRALIBS_HTML)',
    'adv' : '$(PLUGIN_ADV_EXTRALIBS)',
    'media' : '$(EXTRALIBS_MEDIA)',
    'stc' : '$(EXTRALIBS_STC)',
    'webview' : '$(EXTRALIBS_WEBVIEW)',
}

def mkLibName(wxid):
    """Returns string that can be used as library name, including name
       suffixes, prefixes, version tags etc. This must be kept in sync
       with variables defined in common.bkl!"""
    if wxid == 'mono':
        return '$(WXNAMEPREFIXGUI)$(WXNAMESUFFIX)$(WXVERSIONTAG)$(HOST_SUFFIX)'
    if wxid == 'base':
        return '$(WXNAMEPREFIX)$(WXNAMESUFFIX)$(WXVERSIONTAG)$(HOST_SUFFIX)'
    if wxid in LIBS_NOGUI:
        return f'$(WXNAMEPREFIX)$(WXNAMESUFFIX)_{wxid}$(WXVERSIONTAG)$(HOST_SUFFIX)'
    return f'$(WXNAMEPREFIXGUI)$(WXNAMESUFFIX)_{wxid}$(WXVERSIONTAG)$(HOST_SUFFIX)'

def mkDllName(wxid):
    """Returns string that can be used as DLL name, including name
       suffixes, prefixes, version tags etc. This must be kept in sync
       with variables defined in common.bkl!"""
    if wxid == 'mono':
        return '$(WXDLLNAMEPREFIXGUI)$(WXNAMESUFFIX)$(WXCOMPILER)$(VENDORTAG)$(WXDLLVERSIONTAG)'
    if wxid == 'base':
        return '$(WXDLLNAMEPREFIX)$(WXNAMESUFFIX)$(WXCOMPILER)$(VENDORTAG)$(WXDLLVERSIONTAG)'
    if wxid in LIBS_NOGUI:
        return f'$(WXDLLNAMEPREFIX)$(WXNAMESUFFIX)_{wxid}$(WXCOMPILER)$(VENDORTAG)$(WXDLLVERSIONTAG)'
    return f'$(WXDLLNAMEPREFIXGUI)$(WXNAMESUFFIX)_{wxid}$(WXCOMPILER)$(VENDORTAG)$(WXDLLVERSIONTAG)'


def libToLink(wxlibname):
    """Returns string to pass to <sys-lib> when linking against 'wxlibname'.
       For one of main libraries, libToLink('foo') returns '$(WXLIB_FOO)' which
       must be defined in common.bkl as either nothing (in monolithic build) or
       mkLibName('foo') (otherwise).
       """
    if wxlibname in MAIN_LIBS:
        return f'$(WXLIB_{wxlibname.upper()})'
    else:
        return mkLibName(wxlibname)


def extraLdflags(wxlibname):
    return EXTRALIBS[wxlibname] if wxlibname in EXTRALIBS else ''

wxVersion = None
VERSION_FILE = '../../include/wx/version.h'

def getVersion():
    """Returns wxWidgets version as a tuple: (major,minor,release)."""
    global wxVersion
    if wxVersion is None:
        with open(VERSION_FILE, 'rt') as f:
            lines = f.readlines()
        major = minor = release = None
        for l in lines:
            if not l.startswith('#define'): continue
            splitline = l.strip().split()
            if splitline[0] != '#define': continue
            if len(splitline) < 3: continue
            name = splitline[1]
            value = splitline[2]
            if value is None: continue
            if name == 'wxMAJOR_VERSION':
                major = int(value)
            elif name == 'wxMINOR_VERSION':
                minor = int(value)
            elif name == 'wxRELEASE_NUMBER':
                release = int(value)
            if major != None and minor != None and release != None:
                break
        wxVersion = (major, minor, release)
    return wxVersion

def getVersionMajor():
    return getVersion()[0]
def getVersionMinor():
    return getVersion()[1]
def getVersionRelease():
    return getVersion()[2]


def headersOnly(files):
    """Filters 'files' so that only headers are left. Used with
       <msvc-project-files> to add headers to VC++ projects but not files such
       as arrimpl.cpp."""
    
    def callback(cond, sources):
        prf = suf = ''
        if sources[0].isspace(): prf=' '
        if sources[-1].isspace(): suf=' '
        retval = []
        for s in sources.split():
            if s.endswith('.h'):
                retval.append(s)
        return f"{prf}{' '.join(retval)}{suf}"

    return utils.substitute2(files, callback)


def makeDspDependency(lib):
    """Returns suitable entry for <depends-on-dsp> for main libs."""
    return '%s:$(nativePaths(WXTOPDIR))build\\msw\\wx_%s.dsp' % (lib,lib)
