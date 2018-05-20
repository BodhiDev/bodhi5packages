# -*- coding: utf-8 -*-

# font.py
# font selector test code for eventual use with epad.py
# import time

from efl.elementary import font_properties_get
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl.elementary.table import Table
from efl.elementary.window import StandardWindow
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.check import Check
from efl.elementary.label import Label
from efl.elementary.spinner import Spinner
from efl.elementary.separator import Separator
from efl.elementary.frame import Frame
from efl.elementary.list import List,  ELM_LIST_LIMIT
from efl.elementary.entry import Entry

import locale

locale.setlocale(locale.LC_ALL, '')


EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

class FontSelector(Box):
    def __init__(self, parent_widget, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.cancelCallback = None
        self.actionCallback = None

        self.__first_run = True
        self.use_theme = False
        self.override_theme_font_size = True
        self.override_font_size = 14
        self.theme_data = None
        self.default_font = 'Sans'
        self.default_font_style = 'Regular'
        self.default_font_size = 14
        self.selected_font = self.default_font
        self.selected_font_style = self.default_font_style
        self.selected_font_size = self.default_font_size
        self.font_style_str = self.get_text_style(self.selected_font,
                                             self.selected_font_style,
                                             self.selected_font_size)
        self.preview_text = 'abcdefghijk ABCDEFGHIJK'
        # Font size min and max
        self.fs_min = 8
        self.fs_max = 72

        lb = Label(self, text="<br><hilight><i>Select Font</i></hilight>",
               size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_BOTH)
        lb.show()
        self.pack_end(lb)
        sp = Separator(self, horizontal=True,
                       size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        sp.show()
        self.pack_end(sp)
        # A horizontal box to hold our font list and font styles
        fontBox = Box(self, horizontal=True, homogeneous=True,
                      size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        fontBox.show()
        self.pack_end(fontBox)
        # A vertical box to hold label and list of font families
        vBoxFL = Box(self,
                      size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        vBoxFL.show()
        fontBox.pack_end(vBoxFL)
        # A vertical box to hold label and list of font styles
        vBoxFS = Box(self,
                      size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        vBoxFS.show()
        fontBox.pack_end(vBoxFS)
        # Generate our needed font data
        #now =time.time()
        fonts = []
        fonts_raw = self.evas.font_available_list()
        # populate with default font families
        #   see elm_font_available_hash_add Function in EFL
        f_families = ['Sans', 'Serif', 'Monospace']
        f_styles = ['Regular', 'Italic', 'Bold', 'Bold Italic']
        fonts_raw += [i+':style='+s for i in f_families for s in f_styles]

        self.fonts_hash = {}
        for font in fonts_raw:
            a = font_properties_get(font)
            # if font name contains a '-' a.name will replace with '\\-'
            #   This needs removed to properly display the name
            fn = a.name.replace('\\','')
            fonts.append(fn)
            if fn in self.fonts_hash:
                self.fonts_hash.setdefault(fn, []).append(a.styles[0])
            else:
                self.fonts_hash[fn] = [a.styles[0]]

        # Deal with some problematic special cases
        for a, s in self.fonts_hash.items():
           #print(a,s)
           if s:
            if len(s) == 1:
                s[0]=s[0].rstrip()
                if s[0] == u'regular':
                    s[0] =  u'Regular'
                if s[0] == u'Medium Italic':
                    self.fonts_hash.setdefault(a, []).append(u'Bold Italic')
                elif s[0]== u'Italic':
                    if a != u'Romande ADF Script Std':
                       self.fonts_hash.setdefault(a, []).append(u'Regular')
                       self.fonts_hash.setdefault(a, []).append(u'Bold')
                    self.fonts_hash.setdefault(a, []).append(u'Bold Italic')
                else:
                    self.fonts_hash.setdefault(a, []).append(u'Italic')
                    self.fonts_hash.setdefault(a, []).append(u'Bold')
                    self.fonts_hash.setdefault(a, []).append(u'Bold Italic')
            elif len(s) == 2:
                if any(u'Oblique' in w for w in s):
                    if a not in {u'Baskervald ADF Std Heavy', u'Latin Modern Roman Demi'}:
                        self.fonts_hash.setdefault(a, []).append(u'Bold')
                        self.fonts_hash.setdefault(a, []).append(u'Bold Oblique')
                elif any(u'Italic' in w for w in s):
                    self.fonts_hash.setdefault(a, []).append(u'Bold')
                    self.fonts_hash.setdefault(a, []).append(u'Bold Italic')
                else:
                    self.fonts_hash.setdefault(a, []).append(u'Italic')
                    self.fonts_hash.setdefault(a, []).append(u'Bold Italic')
            elif len(s) == 3 and set(s)== {u'Bold', u'Oblique', u'Medium'}:
                # case GWMonospace
                self.fonts_hash.setdefault(a, []).append(u'Bold Oblique')
            elif len(s) == 3 and set(s) == {u'Italic', u'Regular', u'Bold'}:
               # Case Eden Mills
               self.fonts_hash.setdefault(a, []).append(u'Bold Italic')
            elif len(s) < 4:
                    print ("may need fixed Font style for %s: %s" %(a, s))
        #print(self.fonts_hash)

        # for some strange reason many fonts are displayed multiple times. The following lines remove
        # all duplicates and then sort them alphabetically.
        # FIXME: Is this still true
        fonts = list(set(fonts))
        fonts.sort(cmp=locale.strcoll)

        # Elm List for holding font options
        self.font_list = List(self, size_hint_align=FILL_BOTH, size_hint_weight=EXPAND_BOTH, mode=ELM_LIST_LIMIT)
        #self.font_list.callback_selected_add(self.__font_demo_name_set)
        for font in fonts:
            self.font_list.item_append(font.replace('\\',''))
            if font == self.selected_font:
                font_it = self.font_list.last_item_get()
        #print  (time.time()- now)
        self.font_list.go()
        self.font_list.show()

        font_family_label = Label(self)
        font_family_label.text = "<br><b>Font:</b>"
        font_family_label.show()
        vBoxFL.pack_end(font_family_label)
        vBoxFL.pack_end(self.font_list)

        # Elm List for hold font styles
        self.font_style = List(self, size_hint_align=FILL_BOTH, size_hint_weight=EXPAND_BOTH, mode=ELM_LIST_LIMIT)
        #self.font_style.callback_selected_add(self.__font_demo_style_set)

        self.__reset_font_style_list(font_it.text_get())

        self.font_style.go()
        self.font_style.show()

        font_style_label = Label(self)
        font_style_label.text = "<br><b>Style:</b>"
        font_style_label.show()
        vBoxFS.pack_end(font_style_label)
        vBoxFS.pack_end(self.font_style)

        # A table to hold font size Spinner and set theme default Check
        tb = Table(self, homogeneous=True, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        self.pack_end(tb)
        tb.show()

        # spinner to choose the font size
        self.font_sizer = Spinner(self)
        self.font_sizer.min_max_set(self.fs_min, self.fs_max)
        self.font_sizer.value_set(self.selected_font_size)
        #self.font_sizer.callback_changed_add(self.__font_demo_size_set)
        self.font_sizer.show()
        # Label for Spinner
        font_sizer_label = Label(self)
        font_sizer_label.text = "Font Size:  "
        font_sizer_label.show()

        size_box = Box(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        size_box.horizontal_set(True)
        size_box.pack_end(font_sizer_label)
        size_box.pack_end(self.font_sizer)
        size_box.show()
        tb.pack(size_box, 33, 0, 34, 34)

        self.use_theme_ck = Check(self, text="Theme Default   ",size_hint_weight=EXPAND_HORIZ,size_hint_align=(1, 0.5))
        self.use_theme_ck.callback_changed_add(self.__use_theme_checked)
        self.use_theme_ck.show()
        tb.pack(self.use_theme_ck, 67, 0, 33, 34)

        # Entry to hold sample text
        self.font_demo = Entry(self, single_line = True, editable= False, context_menu_disabled = True,
                               text = self.preview_text, scrollable = True,
                               size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        self.font_demo.show()

        demo_box = Frame(self, size_hint_align=FILL_BOTH, text="Preview:", content=self.font_demo)
        demo_box.show()

        # Fixme: move this shit
        font_it.selected_set(True)
        font_it.show()
        # Ensure focus is on Font List
        self.font_list.focus_set(True)
        self.pack_end(demo_box)

        # cancel and OK buttons
        ok_button = Button(self)
        ok_button.text = "OK"
        ok_button.callback_pressed_add(self.__ok_button_pressed)
        ok_button.show()

        cancel_button = Button(self)
        cancel_button.text = "Cancel"
        cancel_button.callback_pressed_add(self.__cancel_button_pressed)
        cancel_button.show()

        # box for buttons
        button_box = Box(self)
        button_box.horizontal_set(True)
        button_box.show()
        button_box.pack_end(cancel_button)
        button_box.pack_end(ok_button)
        self.pack_end(button_box)

    def callback_activated_add(self, cb):
        self.actionCallback = cb

    def callback_cancel_add(self, cb):
        self.cancelCallback = cb

    def set_preview_text(self, text):
        self.preview_text = text
        self.font_demo.entry_set(text)

    def __cancel_button_pressed(self, btn):
        self.use_theme = self.show.use_theme_init
        #print("cancel", self.use_theme)
        self.selected_font = self.default_font
        self.selected_font_style = self.default_font_style
        self.selected_font_size = self.default_font_size
        self.font_style_str = self.get_text_style(self.selected_font,
                                             self.selected_font_style,
                                             self.selected_font_size)
        if self.cancelCallback:
            self.cancelCallback(self)

    def __ok_button_pressed(self, btn):
        # Set selections
        # if use_theme is set any of these could be potentially unset
        try:
            self.selected_font       = self.font_list.selected_item_get().text_get()
            self.selected_font_style = self.font_style.selected_item_get().text_get()
            self.selected_font_size  = self.font_sizer.value_get()
            self.font_style_str = self.get_text_style(self.selected_font,
                                                 self.selected_font_style,
                                                 self.selected_font_size)
        except AttributeError:
            self.selected_font = self.default_font
            if self.default_font_style in self.fonts_hash[self.selected_font]:
                self.selected_font_style = self.default_font_style
            else:
                #print("OK attribute error", self.selected_font, self.default_font_style)
                self.selected_font_style = self.fonts_hash.items[self.selected_font][0]
            self.selected_font_size = self.default_font_size
            self.font_style_str = self.get_text_style(self.selected_font,
                                                 self.selected_font_style,
                                                 self.selected_font_size)
        self.use_theme = self.use_theme_ck.state_get()
        if self.actionCallback:
            self.actionCallback(self)

    def __use_theme_checked(self, ck):
        self.use_theme = ck.state_get()
        #print ( '__use_theme_checked')
        if self.use_theme:
            if not self.theme_data:
                self._set_theme_data()
            self.set_font(*self.theme_data)
            while self.font_demo.text_style_user_peek():
                self.font_demo.text_style_user_pop();
            if self.theme_data[1] == None:
                try:
                    self.font_style.selected_item_get().selected = False
                except AttributeError:
                    pass
            if self.override_theme_font_size:
                self.font_demo.text_style_user_push("DEFAULT='font_size={0}'".format(self.override_font_size))
                self.font_sizer.value_set(self.override_font_size)
            # Ensure these are unchanged
            ck.state = self.use_theme = True
        else:
            # ensure style is selected
            self.selected_font = self.default_font
            self.selected_font_style = self.default_font_style
            self.selected_font_size = self.default_font_size
            self.font_style_str = self.get_text_style(self.selected_font,
                                             self.selected_font_style,
                                             self.selected_font_size)

            self.set_font(self.default_font, self.default_font_style, self.default_font_size)
            # Ensure these are unchanged
            ck.state = self.use_theme = False


    def _set_theme_data(self):
        tb_style = self.font_demo.textblock.style_get()

        font = tb_style.split('text_class=entry_text')[1].split('font=')[1].split("'em=")[0]
        # font may or may not have style associated with it
        if ':style=' in font:
            font, style = font.split(':style=')
        else:
            style = None
        # If font name or styyle has spaces in it
        #   textblock.style_get() inserts '\' before space
        #   then the python string split function adds another space
        # To set the style with a font name that has spaces spaces need to be removed
        font = font.replace('\\ ',' ')
        if style:
            style = style.replace('\\ ',' ')
        size = tb_style.split('text_class=entry_text')[1].split('font_size=')[1].split(' ')[0]
        self.theme_data = [font, style, float(size)]

    def set_font(self, font, style=None, size=None):
        found_font = found_style = False

        #print(self.set_font.__name__, font, style, size, self.use_theme)
        for font_it in self.font_list.items:
            if '\\' in font:
                # Special characters in font names cause problems
                #   need to remove the escape characters before comparison 
                font = font.replace('\\','')
            if font == font_it.text:
                found = True
                self.selected_font = font_it.text
                font_it.selected = True
                font_it.show()
                break
        if size and self.fs_min <= size <= self.fs_max:
            self.selected_font_size = size
            self.font_sizer.value_set(size)
        if found_font:
            self.__reset_font_style_list(font)
            if style in self.fonts_hash[font_it.text]:
                for style_it in self.font_style.items:
                    if style == style_it.text:
                        self.selected_font_style = style_it.text
                        style_it.selected = True
                        style_it.show()
                        found_style = True
                        break
        
        if not found_style:
            self.__font_style_set(self.selected_font)
        # Ensure focus is on Font List
        self.font_list.focus_set(True)

    def __font_demo_name_set(self, f_list, font):

        if self.use_theme:
            self.use_theme = self.use_theme_ck.state = False
        self.__reset_font_style_list(font.text_get())
        self.__font_style_set(font.text_get())
        # Ensure focus is on Font List
        self.font_list.focus_set(True)

    def __font_demo_style_set(self, s_list, style):
        if self.use_theme:
            self.use_theme = self.use_theme_ck.state = False
        self.__font_style_set(self.font_list.selected_item_get().text_get())

    def __font_demo_size_set(self, sizer):
        if self.use_theme:
            self.use_theme = self.use_theme_ck.state = False
        self.__font_style_set(self.font_list.selected_item_get().text_get())

    def __font_style_set(self, font_name):
        #print (" __font_style_set", font_name)
        while self.font_demo.text_style_user_peek():
            self.font_demo.text_style_user_pop();

        if self.font_style.selected_item_get():
            font_style = self.font_style.selected_item_get().text_get()
        else:
            font_style = self.font_style.first_item_get().text_get()

        font_size = self.font_sizer.value_get()

        style = self.get_text_style(font_name, font_style, font_size)
        self.font_demo.text_style_user_push(style)
        self.font_style_str = style

    def __reset_font_style_list(self, font_name):
        self.font_style.clear()
        self.__normalize_font_style_list(font_name)
        for style in self.fonts_hash[font_name]:
            self.font_style.item_append(style)
            if font_name == self.default_font and style == self.selected_font_style:
                self.font_style.last_item_get().selected_set(True)
        if font_name != self.default_font:
            self.font_style.first_item_get().selected_set(True)
        #print(self.font_style.first_item_get())
        #self.font_style.first_item_get().selected_set(True)
        self.font_style.first_item_get().show()


    def get_text_style(self, font_name, font_style_str, font_size):
        if "'" in font_name:
            # Special characters in font name issue
            font_name = font_name.replace("'", "\\'")
        if font_style_str:
            style = "DEFAULT='font_size={0} font={1}:style={2}'".format(font_size, font_name.replace(' ','\ '), font_style_str.replace(' ','\ '))
        else:
            style = "DEFAULT='font_size={0} font={1}'".format(font_size, font_name.replace(' ','\ '))
        return style

    def __normalize_font_style_list(self, font_name):
        styles_list = self.fonts_hash[font_name]
        if 'Regular' in styles_list and styles_list[0] != 'Regular':
            styles_list.remove('Regular')
            styles_list.insert(0, 'Regular')

    def show(self):
        #print("SHOW  Selected ", self.use_theme, self.selected_font, self.selected_font_style)
        #print("SHOW  default ", self.use_theme, self.default_font, self.default_font_style)
        if self.__first_run:
            # only set the callbacks once
            # needed when called from another window repeatedly
            #print("__first_run__")
            self.font_list.callback_selected_add(self.__font_demo_name_set)
            self.font_style.callback_selected_add(self.__font_demo_style_set)
            self.font_sizer.callback_changed_add(self.__font_demo_size_set)
            self.__first_run = False
        self.show.__func__.use_theme_init = self.use_theme
        self.use_theme_ck.state = self.use_theme
        if self.use_theme:
            self.__use_theme_checked(self.use_theme_ck)
        #print("selected", self.font_list.selected_item_get().text_get())
        if not self.use_theme:
            self.set_font(self.selected_font,self.selected_font_style, self.selected_font_size)
        super(FontSelector, self).show()
