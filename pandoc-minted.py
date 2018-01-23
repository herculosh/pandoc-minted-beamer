#!/usr/bin/env python
"""A pandoc filter to use minted for typesetting code in the LaTeX mode."""

from string import Template

from pandocfilters import Header, RawBlock, RawInline, toJSONFilters

def unpack_metadata(meta):
    ''' Unpack the metadata to get pandoc-minted settings.

    Args:
        meta    document metadata
    '''
    settings = meta.get('pandoc-minted', {})
    if settings.get('t', '') == 'MetaMap':
        settings = settings['c']

        # Get language.
        language = settings.get('language', {})
        if language.get('t', '') == 'MetaInlines':
            language = language['c'][0]['c']
        else:
            language = None

        return {'language': language}

    else:
        # Return default settings.
        return {'language': 'text'}


def unpack_code(value, language):
    ''' Unpack the body and language of a pandoc code element.

    Args:
        value       contents of pandoc object
        language    default language
    '''
    [[_, classes, attributes], contents] = value

    if len(classes) > 0:
        language = classes[0]

    attributes = ', '.join('='.join(x) for x in attributes)

    return {'contents': contents, 'language': language,
            'attributes': attributes}


def fragile(key, value, format, meta):
    """Make headers/frames fragile."""
    if format != 'beamer':
        return

    if key == 'Header':
        level, meta, contents = value
        # Add the attribute
        meta[1].append('fragile')
        return Header(level, meta, contents)


def minted(key, value, format, meta):
    """Use minted for code in LaTeX."""
    if format != 'latex' and format != 'beamer':
        return

    if key == 'CodeBlock':
        template = Template('\\begin{minted}[autogobble,breaklines,$attributes]{$language}\n$contents\n\end{minted}')
        Element = RawBlock
    elif key == 'Code':
        template = Template('\\mintinline[autogobble,breaklines,$attributes]{$language}{$contents}')
        Element = RawInline
    else:
        return

    settings = unpack_metadata(meta)
    code = unpack_code(value, settings['language'])

    text = template.substitute(code)
    return Element('latex', text)


if __name__ == '__main__':
    toJSONFilters([fragile, minted])
