import click
import json

import users.api
import users

from cli import libreant_cli_common

usersDB = None
conf = dict()


@click.group(name="libreant-users", help="manage libreant users")
@libreant_cli_common()
def libreant_users(conf={}, **kwargs):
    global usersDB
    usersDB = users.init_db(conf['USERS_DATABASE'],
                               pwd_salt_size=conf['PWD_SALT_SIZE'],
                               pwd_rounds=conf['PWD_ROUNDS'])
    users.populate_with_defaults()


@libreant_users.group(name='user')
def user_subcmd():
    pass


@user_subcmd.command(name='add')
@click.argument('username')
def user_add(username):
    try:
        users.api.get_user(name=username)
    except users.api.NotFoundException:
        pass
    else:
        click.secho('User already present', err=True)
        exit(1)
    password = click.prompt('Password', hide_input=True,
                            confirmation_prompt=True)
    user = users.api.add_user(username, password)
    click.echo(json.dumps(user.to_dict()))


@user_subcmd.command(name='list')
@click.option('--password', is_flag=True, help='Show also password (in hashed form)')
def user_list(password):
    if password:
        all_users = [{'name': u.name, 'id': u.id, 'pwd_hash': u.pwd_hash} for u in users.User.select()]
    else:
        all_users = [{'name': u.name, 'id': u.id} for u in users.User.select()]
    click.echo(json.dumps(all_users))


@user_subcmd.command(name='show')
@click.argument('username')
def user_show(username):
    u = users.api.get_user(name=username)
    data = u.to_dict()
    data['groups'] = [g.to_dict() for g in u.groups]
    click.echo(json.dumps(data))


@user_subcmd.command(name='passwd', help='change the password for a user')
@click.argument('username')
def user_set_password(username):
    try:
        user = users.api.get_user(name=username)
    except users.api.NotFoundException:
        click.secho('Cannot find user "%s"' % username, err=True)
        exit(1)

    password = click.prompt('Password', hide_input=True,
                            confirmation_prompt=True)
    users.api.update_user(user.id, {'password': password})


@user_subcmd.command(name='check-password',
                        help='check if a password is correct')
@click.argument('username')
def user_check_password(username):
    try:
        user = users.api.get_user(name=username)
    except users.api.NotFoundException:
        click.secho('Cannot find user "%s"' % username, err=True)
        exit(1)

    password = click.prompt('Password', hide_input=True,
                            confirmation_prompt=False)
    if user.verify_password(password):
        click.secho('Password correct', fg='green')
    else:
        click.secho('Incorrect password for "%s"' % username,
                    fg='red', err=True)


@user_subcmd.command(name='delete')
@click.argument('username')
def user_del(username):
    u = users.api.get_user(name=username)
    users.api.delete_user(u.id)


@libreant_users.group(name='group')
def group_subcmd():
    pass


@group_subcmd.command(name='delete')
@click.argument('groupname')
def group_del(groupname):
    u = users.api.get_group(name=groupname)
    users.api.delete_group(u.id)


@group_subcmd.command(name='create')
@click.argument('groupname')
def group_add(groupname):
    try:
        users.api.get_group(name=groupname)
    except users.api.NotFoundException:
        pass
    else:
        click.secho('Group already present', err=True)
        exit(1)
    group = users.api.add_group(groupname)
    click.echo(json.dumps(group.to_dict()))


@group_subcmd.command(name='list', help='List groups')
def list_groups():
    click.echo(json.dumps([g.to_dict() for g in users.Group.select()]))


@group_subcmd.command(name='show', help='Show group properties and members')
@click.argument('groupname')
def show_group(groupname):
    group = users.api.get_group(name=groupname)
    groupdict = group.to_dict()
    groupdict['users'] = [u.to_dict() for u in users.api.get_users_in_group(group.id)]
    click.echo(json.dumps(groupdict))


@group_subcmd.command(name='user-remove', help='Remove a user from a group')
@click.argument('username')
@click.argument('groupname')
def remove_from_group(username, groupname):
    u = users.api.get_user(name=username)
    g = users.api.get_group(name=groupname)
    users.api.remove_user_from_group(u.id, g.id)
    userdata = u.to_dict()
    userdata['groups'] = [ug.to_dict() for ug in
                          users.api.get_groups_of_user(u.id)]
    click.echo(json.dumps(userdata))


@group_subcmd.command(name='user-add', help='Add a user to a group')
@click.argument('username')
@click.argument('groupname')
def add_to_group(username, groupname):
    u = users.api.get_user(name=username)
    g = users.api.get_group(name=groupname)
    users.api.add_user_to_group(u.id, g.id)
    userdata = u.to_dict()
    userdata['groups'] = [ug.to_dict() for ug in users.api.get_groups_of_user(u.id)]
    click.echo(json.dumps(userdata))


@libreant_users.group(name='capability')
def caps_subcmd():
    pass


@group_subcmd.command(name='caplist', help='List capabilities owned by group')
@click.argument('groupname')
def list_capabilities(groupname):
    group = users.api.get_group(name=groupname)
    click.echo(json.dumps([c.to_dict() for c in group.capabilities]))


@group_subcmd.command(name='cap-add', help='Add a new capability to a group')
@click.argument('groupname')
@click.argument('domain')
@click.argument('action')
def capability_add(groupname, domain, action):
    possibleactions = {v[0]: v for v in users.Action.ACTIONS}
    action = '' if action == '0' else action
    action = [possibleactions[x] for x in action]
    action = users.Action.from_list(action)

    group = users.api.get_group(name=groupname)
    cap = users.api.add_capability(domain, action)
    users.api.add_capability_to_group(cap.id, group.id)

    group = users.api.get_group(name=groupname)
    groupdata = group.to_dict()
    groupdata['capabilities'] = [c.to_dict() for c in group.capabilities]
    click.echo(json.dumps(groupdata))


@caps_subcmd.command(name='delete')
@click.argument('capID')
def capability_del(capid):
    users.api.delete_capability(capid)


@caps_subcmd.command(name='list', help='List every capability')
def capability_list():
    allcaps = users.Capability.select()
    click.echo(json.dumps([c.to_dict() for c in allcaps]))
