#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def _lxmlns(nsmap: dict, ns_prefix: str) -> str:
    """Returns namespace value for given prefix.

    Looks up the namespace value given a dictionary and the key (=ns_prefix).

    Return is in format: "{namespace}".

    Args:
        nsmap: The nsmap.
        ns_prefix: The prefix of the namespace. This is a key of the nsmap.

    Returns:
        The namespace value.
    """
    return f"{{{nsmap[ns_prefix]}}}"


def qname_text(nsmap: dict, ns_prefix: str, local_name: str) -> str:
    """Returns the QNAME text.

    The QNAME text has the following format: {namespace}localname.
    E.g. {http://www.w3.org/1999/xhtml}html.

    Args:
        nsmap: The nsmap.
        ns_prefix: The prefix of the namespace. This is a key of the nsmap.
        local_name: The local name.

    Returns:
        The QNAME text.
    """
    return f"{_lxmlns(nsmap, ns_prefix)}{local_name}"
