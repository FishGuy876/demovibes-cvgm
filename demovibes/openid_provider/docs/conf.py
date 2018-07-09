# -*- coding: utf-8 -*-
#

templates_path = ['.templates']

source_suffix = '.rst'
source_encoding = 'utf-8'

master_doc = 'index'

project = 'Django OpenID Provider'
_author = u"Roman Barczyński"
copyright = u"2010, %s" % _author
release = 'v0.2'

pygments_style = 'sphinx'


html_style = 'default.css'
html_title =  "%s documentation" % (project)
html_static_path = ['.static']
html_last_updated_fmt = '%b %d, %Y'

html_use_modindex = False
html_use_index = False
html_copy_source = False
html_file_suffix = '.html'

# Options for LaTeX output
# ------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  (master_doc, 'openid_provider.tex', '%s Documentation' % project, _author, 'howto'), # 'manual' or 'howto'
]

latex_elements = {
	'papersize': 'a4',
	'pointsize': '10pt',
	'fncychap': '\\usepackage{fancyhdr}',
	'preamble': '\\pagenumbering{arabic}'
}

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True
