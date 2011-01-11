/**
 * This file is a part of MediaCore, Copyright 2010 Simple Station Inc.
 *
 * MediaCore is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * MediaCore is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * This file defines the signatures of functions and prototypes that are
 * provided by third party libraries, but used in code that will be compiled
 * with the closure compiler.
 *
 * Defining variables here will prevent them being renamed in the compiled
 * code.
 *
 * See: http://code.google.com/closure/compiler/docs/api-tutorial3.html#externs
 */

/**
 * The main jwplayer library init function and methods.
 * From scripts/third-party/jw_player/jwplayer.js
 */
var jwplayer = function(jwplayerOpts){};
jwplayer.prototype.getHeight = function(){};
jwplayer.prototype.getWidth = function(){};
jwplayer.prototype.resize = function(){};
jwplayer.prototype.setup = function(){};
