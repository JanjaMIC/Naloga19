#!/usr/bin/env python
import os
import jinja2
import webapp2

from models import Guestbook


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")


class PosljiSporociloHandler(BaseHandler):
    def post(self):
        uporabnikovo_ime = self.request.get("ime")
        uporabnikov_priimek = self.request.get("priimek")
        uporabnikov_email = self.request.get("email")
        uporabnikovo_sporocilo = self.request.get("tekst")

        if uporabnikovo_ime == "":
           uporabnikovo_ime = "neznanec"

        sporocilo = Guestbook(ime=uporabnikovo_ime, priimek=uporabnikov_priimek, email=uporabnikov_email, tekst=uporabnikovo_sporocilo)
        sporocilo.put()

        return self.render_template("guestbook_poslano.html")


class PrikaziSporocilaHandler(BaseHandler):
    def get(self):
        vsi_vnosi = Guestbook.query().order(Guestbook.ustvarjeno).fetch()

        view_vars = {
            "vsi_vnosi": vsi_vnosi
        }

        return self.render_template("prikazi_vnose.html", view_vars)


class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))

        view_vars = {
            "sporocilo": sporocilo
        }

        return self.render_template("posamezen_vnos.html", view_vars)


class UrediSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))

        view_vars = {
            "sporocilo": sporocilo
        }

        return self.render_template("uredi_sporocilo.html", view_vars)

    def post(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        sporocilo.ime = self.request.get("ime")
        sporocilo.tekst = self.request.get("tekst")
        sporocilo.put()

        self.redirect("/sporocilo/" + sporocilo_id)

class IzbrisiSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        view_vars = {
            "sporocilo": sporocilo
        }

        return self.render_template("izbrisi_sporocilo.html", view_vars)

    def post(self, sporocilo_id):
        sporocilo = Guestbook.get_by_id(int(sporocilo_id))
        sporocilo.key.delete()

        self.redirect("/prikazi_vnose")



app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/guestbook_poslano', PosljiSporociloHandler),
    webapp2.Route('/prikazi_vnose', PrikaziSporocilaHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
], debug=True)
