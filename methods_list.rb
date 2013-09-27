begin; require 'rubygems'; rescue LoadError; end
require 'appscript'

itu = Appscript.app("iTunes.app")

puts "--------------"
puts "ITUNES METHODS"
puts "--------------"
itu.methods.sort.each { |m|
  p m
}

puts "\n---------------------"
puts "ITUNES TRACK METHODS"
puts "---------------------"
itu.current_track.methods.sort.each { |m|
  p m
}