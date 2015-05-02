#!/usr/bin/env python

import os, sys

filepath = os.path.abspath(__file__)
fullpath = os.path.dirname(filepath) + '/'

exec(open(fullpath + "gsettings.conf").read())
exec(open(fullpath + "mysettings.conf").read())

PATH_GLOSS = fullpath + PATH_GLOSS

if PATH_MYLIB:
    sys.path.append(PATH_MYLIB)
    from debugly import *

from gi.repository import Gtk, Gdk, Pango
import browselst2 as BL
import viewer2 as Vi

#   ____ _   _ ___
#  / ___| | | |_ _|
# | |  _| | | || |
# | |_| | |_| || |
#  \____|\___/|___|

class GUI(Gtk.Grid):
    def __init__(self, parent=None):
        Gtk.Grid.__init__(self)
        self.parent = parent

        self.CLIP_CYCLE = None
        self.TAB_LST = []
        self.FOUND_ITEMS = []
        self.CURRENT_TAB = 0

        self.SPELL_CHECK = True
        self.SMART_COPY = True
        self.TRANSLITERATE = True

        self.makeWidgets()


    def makeWidgets(self):
        self.attach(self.makeWidgets_toolbar(), 0, 0, 3, 1)
        self.attach(self.makeWidgets_searchbar(), 1, 1, 1, 1)
        # self.attach(self.makeWidgets_sidebar(), 0, 1, 1, 2)
        self.attach(self.makeWidgets_viewer(), 1, 2, 1, 1)
        # self.attach(self.makeWidgets_settings(), 0, 3, 2, 1)
        self.attach(self.makeWidgets_browser(LIST_GLOSS[0]), 0, 4, 2, 1)


    def makeWidgets_toolbar(self):
        toolbar = Gtk.Toolbar()
        #
        ## About Button
        self.button_about = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ABOUT)
        # button_about.connect("clicked", self.on_clear_clicked)
        toolbar.insert(self.button_about, 0)
        ##
        #
        ##
        toolbar.insert(Gtk.ToolButton.new_from_stock(Gtk.STOCK_PREFERENCES), 0)
        ##
        #
        toolbar.insert(Gtk.SeparatorToolItem(), 0)
        #
        ## Clean Viewer
        self.button_clear = Gtk.ToolButton.new_from_stock(Gtk.STOCK_CLEAR)
        toolbar.insert(self.button_clear, 0)
        self.button_clear.connect("clicked", self._clean_button)
        ##
        #
        ## Add Button
        self.button_add = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
        toolbar.insert(self.button_add, 0)
        self.button_add.connect("clicked", lambda w: add_to_gloss(self.parent))
        ##
        #
        toolbar.insert(Gtk.SeparatorToolItem(), 0)
        #
        ## Smart Copy Toggle Button
        self.toggle_copy = Gtk.ToggleToolButton.new_from_stock(Gtk.STOCK_COPY)
        toolbar.insert(self.toggle_copy, 0)
        self.toggle_copy.set_active(self.SMART_COPY)
        self.toggle_copy.connect("toggled", self._smart_copy_toggle, '1')
        ##
        #
        ## Spell-check Toggle Button
        self.toggle_spell = Gtk.ToggleToolButton.new_from_stock(Gtk.STOCK_SPELL_CHECK)
        toolbar.insert(self.toggle_spell, 0)
        self.toggle_spell.set_active(True)
        self.toggle_spell.connect("toggled", self._spell_check_toggle, '1')
        ##
        #
        ## Auto Transliterate Button
        self.toggle_trans = Gtk.ToggleToolButton.new_from_stock(Gtk.STOCK_CONVERT)
        toolbar.insert(self.toggle_trans, 0)
        self.toggle_trans.set_active(True)
        self.toggle_trans.connect("toggled", self._spell_check_toggle, '1')
        ##
        #
        toolbar.insert(Gtk.SeparatorToolItem(), 0)
        #
        ## Button Forward Button
        self.button_forward = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_FORWARD)
        toolbar.insert(self.button_forward, 0)
        self.button_forward.connect("clicked", lambda e: self._forward_click())
        self.button_forward.set_sensitive(False)
        ##
        #
        ## Button Back Button
        self.button_back = Gtk.ToolButton.new_from_stock(Gtk.STOCK_GO_BACK)
        toolbar.insert(self.button_back, 0)
        self.button_forward.connect("clicked", lambda e: self._back_click())
        self.button_back.set_sensitive(False)

        return toolbar


    def _back_click(self):
        print("back clicked")
        self.button_forward.set_sensitive(True)


    def _forward_click(self):
        print("forward clicked")


    def _transliterate_toggle(self, *args):
        self.TRANSLITERATE = not self.TRANSLITERATE


    def _spell_check_toggle(self, *args):
        self.SPELL_CHECK = not self.SPELL_CHECK


    def _smart_copy_toggle(self, *args):
        self.SMART_COPY = not self.SMART_COPY


    def _clean_button(self, widget):
        self.viewer.textbuffer.set_text("")
        self.cb_dropdown.clear()


    def makeWidgets_searchbar(self):
        layout = Gtk.HBox()

        label = Gtk.Label()
        label.set_markup("<b>Query</b>")
        layout.add(label)

        self.search_history = []
        self.cb_dropdown = Gtk.ListStore(str)
        self.cb_search = Gtk.ComboBox.new_with_model_and_entry(self.cb_dropdown)
        self.cb_search.set_entry_text_column(0)
        layout.add(self.cb_search)

        ### binding
        self.cb_search.connect('key_release_event', self.searchbar_binds)
        accel_search = Gtk.AccelGroup()
        root.add_accel_group(accel_search)
        self.cb_search.add_accelerator("grab_focus", accel_search, ord('f'), Gdk.ModifierType.CONTROL_MASK, 0)

        ## Button
        self.b_search = Gtk.Button(label="Search", stock=Gtk.STOCK_FIND)
        layout.add(self.b_search)
        self.b_search.connect('clicked', self.searchWord)

        return layout


    def searchbar_binds(self, widget, event):
        # print(event.keyval)
        if event.keyval == 65293: # <enter> return
            self.searchWord()

        if Gdk.ModifierType.CONTROL_MASK & event.state:
            if event.keyval == ord('c'):
                entry = self.cb_search.get_child()
                entry.set_text("")


    def makeWidgets_sidebar(self):
        layout = Gtk.VBox()

        self.gloss_list = Gtk.ListStore(str)
        for gloss in LIST_GLOSS:
            self.gloss_list.append([gloss])

        self.cb_gloss = Gtk.ComboBox(model=self.gloss_list)
        layout.add(self.cb_gloss)

        scroll = Gtk.ScrolledWindow()
        layout.add(scroll)
        scroll.set_vexpand(False)

        self.liststore = Gtk.ListStore(str)
        self.treeview = Gtk.TreeView(model=self.liststore)
        scroll.add(self.treeview)
        renderer_text = Gtk.CellRendererText()
        c0 = Gtk.TreeViewColumn("Suggestions", renderer_text, text=0)
        self.treeview.append_column(c0)
        self.liststore.append(["hello"])
        self.liststore.append(["world"])

        return layout


    def makeWidgets_viewer(self):
        self.viewer = Vi.Viewer(self)
        # self.viewer.connect('key_press_event', self.viewer_binds)
        # self.viewer.textview.override_font(Pango.font_description_from_string('DejaVu Sans Mono 12'))
        self.viewer.textview.modify_font(Pango.font_description_from_string('DejaVu Sans Mono 12'))
        return self.viewer


    def makeWidgets_settings(self):
        layout = Gtk.HBox()

        self.font_button = Gtk.FontButton()
        layout.add(self.font_button)
        self.font_button.set_font_name('DejaVu Sans Mono 12')
        self.font_button.connect('font-set', lambda w: self.viewer.modify_font(w.get_font_desc()))

        # SHOW HIDE GLOSS
        #toolbar.insert(Gtk.ToolButton.new_from_stock(Gtk.STOCK_GOTO_TOP), 0)
        # toolbar.insert(Gtk.ToolButton.new_from_stock(Gtk.STOCK_GOTO_BOTTOM), 0)

        layout.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_CLOSE))
        layout.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_APPLY))

        return layout


    def makeWidgets_browser(self, gloss):
        self.GLOSS = PATH_GLOSS + gloss
        self.notebook = Gtk.Notebook()
        tab = 0
        for file_name in os.listdir(self.GLOSS):
            if not file_name[-4:] in FILE_TYPES: continue
            if "main.tra" in file_name: self.MAIN_TAB = tab
            obj = BL.BrowseList(self.parent, self.GLOSS + file_name)
            self.notebook.append_page(obj, Gtk.Label(label=file_name[:-4]))
            self.TAB_LST.append(obj)
            tab += 1
        return self.notebook


    def searchWord(self, *args):
        ## TODO: Reverse search in nepali
        # grep might be useful for quick implementation
        entry = self.cb_search.get_child()
        query = entry.get_text().strip().lower()
        if not query: return

        clip_out = []
        self.FOUND_ITEMS.clear()
        for word in query.split():
            foundFlag = False
            for tab, obj in enumerate(self.TAB_LST):
                for item in obj.liststore:
                    if word not in item[1]: continue
                    row = [tab] + list(item)
                    clip_out += self.viewer.parser(row)
                    foundFlag = True
                    self.FOUND_ITEMS.append(row)
                    self.cb_dropdown.insert(0, [word])

            if foundFlag is False:
                self.viewer.not_found(word)

        if len(clip_out) == 0:
            self.viewer.jump_to_end()
            return

        if len(self.cb_dropdown) > 1:
            self.button_back.set_sensitive(True)

        self.viewer.mark_found(clip_out[0])
        self.CLIP_CYCLE = circle(clip_out)
        self.cb_search.grab_focus()

        if not self.SMART_COPY: return

        global clipboard, diff
        diff = 1
        curr = next(self.CLIP_CYCLE)
        clipboard.set_text(curr, -1)


    def open_dir(self):
        os.system("nemo %s"%(self.GLOSS))


    def reload(self, gloss):
        if self.GLOSS == PATH_GLOSS + gloss:
            xcowsay()
            return

        self.remove(gui.notebook)
        del gui.notebook
        for obj in self.TAB_LST:
            del obj
        self.TAB_LST.clear()

        gui.attach(gui.makeWidgets_browser(gloss), 0, 4, 2, 1)
        root.show_all()
        gui.searchWord()


def add_to_gloss(parent):
    entry = gui.cb_search.get_child()
    word = entry.get_text().strip().lower()

    dialogWindow = Gtk.MessageDialog(parent,
                                     Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                     Gtk.MessageType.QUESTION,
                                     Gtk.ButtonsType.OK_CANCEL,
                                     "translate of '%s'"%word)
    dialogWindow.set_title("Add to gloss")

    dialogBox = dialogWindow.get_content_area()
    userEntry = Gtk.Entry()
    # userEntry.set_visibility(True)
    userEntry.set_size_request(250,0)
    dialogBox.pack_end(userEntry, False, False, 0)

    dialogWindow.show_all()

    response = dialogWindow.run()
    text = userEntry.get_text()
    dialogWindow.destroy()

    if response != Gtk.ResponseType.OK or text == '':
        return None

    row = [word, text]
    obj = gui.browser
    fp = open(obj.GLOSS, 'a').write("\n" + '; '.join(row))
    count = gui.browser.add_to_tree(row)
    gui.viewer.parser([0, count] + row)


def global_key_press(widget, event):
    # print(event.keyval)
    if event.keyval == 65307: Gtk.main_quit() # Esc
    elif event.keyval == 65481: gui.reload(LIST_GLOSS[0]) # F12
    elif event.keyval == 65480: gui.reload(LIST_GLOSS[1]) # F11
    elif event.keyval == 65479: gui.reload(LIST_GLOSS[2]) # F10

    global diff
    if Gdk.ModifierType.CONTROL_MASK & event.state:
        if event.keyval == ord('i'): add_to_gloss(root)
        elif event.keyval == ord('1'): dict_grep()
        elif event.keyval == ord('2'): web_search()
        elif event.keyval == ord('o'): gui.open_dir()
        elif event.keyval == ord('l'): gui._clean_button(gui.viewer)
        elif event.keyval == ord('r'):
            if gui.CLIP_CYCLE:
                diff = -1
                text = next(gui.CLIP_CYCLE)
                gui.viewer.mark_found(text)
                if gui.SMART_COPY:  clipboard.set_text(text, -1)
            else: gui.cb_search.grab_focus()
        elif event.keyval == ord('s'):
            if gui.CLIP_CYCLE:
                diff = 1
                text = next(gui.CLIP_CYCLE)
                gui.viewer.mark_found(text)
                if gui.SMART_COPY:  clipboard.set_text(text, -1)
            else: gui.cb_search.grab_focus()
        elif event.keyval == ord('v'):
            text = clipboard.wait_for_text()
            entry = gui.cb_search.get_child()
            entry.set_text(text.strip().lower())
            gui.cb_search.grab_focus()
            gui.searchWord()
        elif event.keyval == ord('u'):
            t, _id, *etc = gui.FOUND_ITEMS[0] if gui.FOUND_ITEMS else [ gui.CURRENT_TAB, 0 ]
            gui.TAB_LST[t].open_gloss(_id)
        return


    if Gdk.ModifierType.META_MASK and event.state:
        if ord('1') <= event.keyval <= ord('9'):
            t = event.keyval - ord('1')
            gui.notebook.set_current_page(t) # TODO range check not needed
        elif event.keyval == ord('0'):
            gui.notebook.set_current_page(gui.MAIN_TAB)



diff = 1
def circle(iterable):
    saved = iterable[:]
    i = -1
    global diff
    while saved:
        l = len(saved)
        i += diff
        if diff == 1 and l <= i: i = 0
        if diff == -1 and i < 0: i = l - 1
        yield saved[i]


def main():
    global root
    root = Gtk.Window(title="anubad - अनुवाद")
    root.connect('delete-event', Gtk.main_quit)
    root.connect('key_press_event', global_key_press)
    root.set_default_size(600, 500)

    global gui
    gui = GUI(root)
    gui.cb_search.grab_focus()
    root.add(gui)

    global clipboard
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)


if __name__ == '__main__':
    main()
    if PATH_PLUGINS:
        # TODO: trasliterate, espeak
        PATH_PLUGINS = fullpath + PATH_PLUGINS + '/'
        for file_name in os.listdir(PATH_PLUGINS):
            print("plugin:", file_name)
            exec(open(PATH_PLUGINS + file_name).read())
    root.show_all()
    # NOTE: this is GTK BUG
    gui.notebook.set_current_page(gui.MAIN_TAB)
    gui.CURRENT_TAB = gui.MAIN_TAB
    Gtk.main()
