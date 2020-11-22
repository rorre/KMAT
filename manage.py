import click
import os.path
from kmat import create_app
from kmat.models import Role
from kmat.plugins import db
from flask_migrate import migrate

app = create_app()
app.app_context().push()


@click.group()
def cli():
    pass


@cli.command()
def setup_roles():
    default_role = Role(judge=False, admin=False, submit=True)
    new_roles = [default_role]

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
def setup_database(ctx):
    if os.path.exists("migrations"):
        migrate()
    else:
        db.create_all()
    ctx.invoke(setup_roles)


if __name__ == "__main__":
    cli()
