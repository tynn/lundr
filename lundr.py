#!/usr/bin/env python
# -*- coding: utf-8 -*-
#	This file is part of lundr.
#
#	Copyright (c) 2014 Christian Schmitz <tynn.dev@gmail.com>
#
#	lundr is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	lundr is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with lundr. If not, see <http://www.gnu.org/licenses/>.


''' Test channels of stereo sound '''

__author__ = 'Christian Schmitz'
__author_email__ = 'tynn.dev@gmail.com'
__url__ = 'https://github.com/tynn/lundr'
__version__ = '1.0'

from gi.repository import Gdk, Gst, Gtk


class App (object) :
	""" The lundr application making some noise """

	GLADE = """<interface><object class="GtkWindow" id="window">
		<property name="border_width">10</property>
		<property name="title">L&amp;R</property>
		<property name="resizable">False</property>
		<property name="window_position">mouse</property>
		<property name="icon_name">gtk-close</property>
		<signal name="destroy" handler="__quit__"/>
		<signal name="key-release-event" handler="__key_release__"/>
		<signal name="key-press-event" handler="__key_press__"/>
		<child><object class="GtkBox" id="box">
			<child><object class="GtkEventBox" id="left">
				<signal name="enter-notify-event" handler="__left__"/>
				<signal name="leave-notify-event" handler="__center__"/>
				<child><object class="GtkArrow" id="left_arrow">
					<property name="arrow_type">left</property>
				</object></child>
			</object></child>
			<child><object class="GtkEventBox" id="play_pause">
				<signal name="button-release-event" handler="__play_pause__"/>
				<child><object class="GtkImage" id="play_pause_image">
					<property name="xpad">30</property>
					<property name="stock">gtk-media-play</property>
				</object></child>
			</object></child>
			<child><object class="GtkEventBox" id="right">
				<signal name="enter-notify-event" handler="__right__"/>
				<signal name="leave-notify-event" handler="__center__"/>
				<child><object class="GtkArrow" id="right_arrow"/></child>
			</object></child>
		</object></child>
	</object></interface>"""

	def __init__ (self, wave = 10) :
		""" Sets up the application and calls Gst.init(None) """
		self._event_infos = [False, False, False, False, 0]

		Gst.init(None)
		self.noise = Gst.parse_launch(" ! ".join([
			"audiotestsrc wave=" + str(wave),
			"audiopanorama method=1 name=panorama",
			"alsasink"
		]))
		self.noise.set_state(Gst.State.NULL)
		self.is_playing = False

		self.panorama = self.noise.get_by_name("panorama")

		builder = Gtk.Builder.new_from_string(self.GLADE, -1)
		builder.connect_signals(self)

		self.play_pause_image = builder.get_object("play_pause_image")
		self.left_arrow = builder.get_object("left_arrow")
		self.right_arrow = builder.get_object("right_arrow")

		builder.get_object("window").show_all()

	def set_panorama (self, persistent = False, left = None, right = None) :
		""" Sets the panorama for the noise """
		if persistent :
			if left is not None : self._event_infos[0] = bool(left)
			if right is not None : self._event_infos[1] = bool(right)
		else :
			self._event_infos[2:4] = bool(left), bool(right)

		left = self._event_infos[0] or self._event_infos[2]
		right = self._event_infos[1] or self._event_infos[3]
		panorama = int(right) - int(left)

		if self._event_infos[4] != panorama :
			self._event_infos[4] = panorama
			self.panorama.set_property('panorama', panorama)

			if self.is_playing :
				self.noise.set_state(Gst.State.NULL)
				self.noise.set_state(Gst.State.PLAYING)

			if left == right == False : left = right = True
			self.left_arrow.set_sensitive(left)
			self.right_arrow.set_sensitive(right)

	@staticmethod
	def __quit__ (window) :
		""" Callback for destroy """
		Gtk.main_quit()

	def __play_pause__ (self, event_box, event) :
		""" Callback for play/pause """
		self.is_playing = not self.is_playing

		if self.is_playing :
			state, image = Gst.State.PLAYING, Gtk.STOCK_MEDIA_PAUSE
		else :
			state, image = Gst.State.NULL, Gtk.STOCK_MEDIA_PLAY

		self.noise.set_state(state)
		self.play_pause_image.set_from_stock(image, Gtk.IconSize.BUTTON)

		return True

	def __left__ (self, event_box, event) :
		""" Callback for the left channel """
		self.set_panorama(left = True)
		return True

	def __right__ (self, event_box, event) :
		""" Callback for the right channel """
		self.set_panorama(right = True)
		return True

	def __center__ (self, event_box, event) :
		""" Callback for both channels """
		self.set_panorama(left = False, right = False)
		return True

	def __key_press__ (self, window, event) :
		""" Callback for key_press """
		if not event.state & Gdk.ModifierType.MODIFIER_MASK :
			if event.keyval == Gdk.keyval_from_name("space") :
				self.__play_pause__(self.play_pause_image, event)
				return True
			elif event.keyval == Gdk.keyval_from_name("Left") :
				self.set_panorama(True, left = True)
				return True
			elif event.keyval == Gdk.keyval_from_name("Right") :
				self.set_panorama(True, right = True)
				return True
			elif event.keyval == Gdk.keyval_from_name("Escape") :
				self.__quit__(window)
				return True
		return False

	def __key_release__ (self, window, event) :
		""" Callback for key_release """
		if not event.state & Gdk.ModifierType.MODIFIER_MASK :
			if event.keyval == Gdk.keyval_from_name("Left") :
				self.set_panorama(True, left = False)
				return True
			elif event.keyval == Gdk.keyval_from_name("Right") :
				self.set_panorama(True, right = False)
				return True
			elif event.keyval == Gdk.keyval_from_name("F1") :
				about = Gtk.AboutDialog(
					parent = window,
					program_name = "L&R",
					version = __version__,
					website = __url__,
					copyright = "Copyright © 2014 " + __author__,
					license_type = Gtk.License.GPL_3_0,
					logo_icon_name = None,
				)
				about.run()
				about.destroy()
				return True
		elif event.state & Gdk.ModifierType.CONTROL_MASK :
			if event.keyval == Gdk.keyval_from_name("q") :
				self.__quit__(window)
				return True
			elif event.keyval == Gdk.keyval_from_name("w") :
				self.__quit__(window)
				return True
		return False

	@staticmethod
	def main () :
		""" Resets the signal handler for SIGINT and calls Gtk.main() """
		import signal
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		Gtk.main()


if __name__ == "__main__" : App().main()

