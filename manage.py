import click
import os.path

from kmat import create_app
from kmat.models import Role, User
from kmat.plugins import db
from flask_migrate import migrate

app = create_app()
app.app_context().push()


@click.group()
def cli():
    pass


@cli.command()
def setup_roles():
    default_role = Role(name="Default", submit=True)
    admin_role = Role(name="Admin", admin=True, submit=False)
    judge_role = Role(name="Judge", admin=False, judge=True, submit=False)
    new_roles = [default_role, admin_role, judge_role]

    while True:
        if click.confirm("Do you want to create a new role?"):
            name = click.prompt("Role name")
            color: str = click.prompt("Role color", default="000000")
            if color.startswith("#"):
                color = color[1:]
            click.echo("Would you like it to be able to:")
            judge = click.prompt(" - Judge", type=bool)
            admin = click.prompt(" - Administrate", type=bool)
            submit = click.prompt(" - Submit", type=bool)
            new_role = Role(
                name=name,
                role_color=color,
                judge=judge,
                admin=admin,
                submit=submit,
            )
            new_roles.append(new_role)
        else:
            break

    db.session.add_all(new_roles)
    db.session.commit()


@cli.command()
@click.pass_context
def setup_database(ctx: click.Context):
    if os.path.exists("migrations"):
        migrate()
    else:
        db.create_all()
    ctx.invoke(setup_roles)


@cli.command()
@click.argument("user_id", type=int)
@click.argument("role_id", type=int)
def set_role(user_id: int, role_id: int):
    u = User.query.get(user_id)
    admin_role = Role.query.get(role_id)
    u.roles.append(admin_role)
    db.session.commit()


@cli.command()
@click.argument("user_id", type=int)
@click.pass_context
def set_admin(user_id: int, ctx: click.Context):
    admin_role = None
    temporary_role = None

    role: Role
    for role in Role.query.all():
        if role.name == "Admin":
            admin_role = role

        if role.admin:
            temporary_role = role

    if not admin_role:
        if temporary_role:
            admin_role = temporary_role
        else:
            raise ValueError("No admin role found.")

    ctx.invoke(set_role, user_id=user_id, role_id=admin_role.id)


if __name__ == "__main__":
    cli()
