import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

w = Gtk.Window(title="Tactile Demo")
box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
status = Gtk.Label(label="idle")
entry = Gtk.Entry(); entry.get_accessible().set_name("Name")
btn = Gtk.Button(label="Save"); btn.connect("clicked", lambda *_: status.set_text("saved"))
for x in (entry, Gtk.CheckButton(label="Agree"), btn, status):
    box.add(x)
w.add(box); w.connect("destroy", Gtk.main_quit); w.show_all(); Gtk.main()
