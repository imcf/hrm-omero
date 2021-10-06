"""Functions related to OMERO's tree view."""

from loguru import logger as log


def gen_obj_dict(obj, id_pfx=""):
    """Create a dict from an OMERO object.

    Parameters
    ----------
    obj : omero.gateway._*Wrapper
        The OMERO object to process.
    id_pfx : str, optional
        A string prefix that will be added to the `id` value, by default ''.

    Returns
    -------
    dict
        A dictionary with the following structure:
        ```
            {
                'children': [],
                'id': 'Project:1154',
                'label': 'HRM_TESTDATA',
                'owner': u'demo01',
                'class': 'Project'
            }
        ```
    """
    obj_dict = {}
    obj_dict["label"] = obj.getName()
    obj_dict["class"] = obj.OMERO_CLASS
    if obj.OMERO_CLASS == "Experimenter":
        obj_dict["owner"] = obj.getId()
        obj_dict["label"] = obj.getFullName()
    elif obj.OMERO_CLASS == "ExperimenterGroup":
        # for some reason getOwner() et al. return nothing on a group, so we
        # simply put it to None for group objects:
        obj_dict["owner"] = None
    else:
        obj_dict["owner"] = obj.getOwnerOmeName()
    obj_dict["id"] = id_pfx + f"{obj.OMERO_CLASS}:{obj.getId()}"
    obj_dict["children"] = []
    return obj_dict


def gen_children(conn, omero_id):
    """Get the children for a given node.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    omero_id : hrm_omero.misc.OmeroId
        An object denoting an OMERO target.

    Returns
    -------
    list
        A list with children nodes (of type `dict`), having the `load_on_demand`
        property set to `True` required by the jqTree JavaScript library (except for
        nodes of type `Dataset` as they are the last / lowest level).
    """
    if omero_id.obj_type == "BaseTree":
        return gen_base_tree(conn)

    gid = omero_id.group
    obj_type = omero_id.obj_type
    oid = omero_id.obj_id
    log.debug(f"generating children for: gid={gid} | obj_type={obj_type} | oid={oid}")

    children = []
    conn.SERVICE_OPTS.setOmeroGroup(gid)
    obj = conn.getObject(obj_type, oid)
    # we need different child-wrappers, depending on the object type:
    if obj_type == "Experimenter":
        children_wrapper = conn.listProjects(oid)
    elif obj_type == "ExperimenterGroup":
        log.warning(
            f"{__name__} has been called with omero_id='{str(omero_id)}', but "
            "'ExperimenterGroup' trees should be generated via `gen_group_tree()`!",
        )
        return []

    else:
        children_wrapper = obj.listChildren()

    # now process children:
    for child in children_wrapper:
        children.append(gen_obj_dict(child, "G:" + gid + ":"))

    # set the on-demand flag unless the children are the last level:
    if not obj_type == "Dataset":
        for child in children:
            child["load_on_demand"] = True

    return children


def gen_base_tree(conn):
    """Generate all group trees with their members as the basic tree.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.

    Returns
    -------
    list
        A list of grouptree dicts as generated by `gen_group_tree()`.
    """
    log.debug("Generating base tree...")
    tree = []
    for group in conn.getGroupsMemberOf():
        tree.append(gen_group_tree(conn, group))
    return tree


def gen_group_tree(conn, group=None):
    """Create the tree nodes for a group and its members.

    Parameters
    ----------
    conn : omero.gateway.BlitzGateway
        The OMERO connection object.
    group : omero.gateway._ExperimenterGroupWrapper, optional
        The group object to generate the tree for, by default None which will result in
        the group being derived from the current connection's context.

    Returns
    -------
    dict
        A nested dict of the given group (or the default group if not specified
        explicitly) and its members as a list of dicts in the `children` item, starting
        with the current user as the first entry.
    """
    if group is None:
        log.trace("Getting group from current context...")
        group = conn.getGroupFromContext()

    gid = str(group.getId())
    log.debug(f"Generating tree for group {gid}...")
    conn.setGroupForSession(gid)

    group_dict = gen_obj_dict(group)
    # add the user's own tree first:
    user = conn.getUser()
    user_dict = gen_obj_dict(user, "G:" + gid + ":")
    user_dict["load_on_demand"] = True
    group_dict["children"].append(user_dict)
    # then add the trees for other group members
    for user in conn.listColleagues():
        user_dict = gen_obj_dict(user, "G:" + gid + ":")
        user_dict["load_on_demand"] = True
        group_dict["children"].append(user_dict)
    return group_dict
