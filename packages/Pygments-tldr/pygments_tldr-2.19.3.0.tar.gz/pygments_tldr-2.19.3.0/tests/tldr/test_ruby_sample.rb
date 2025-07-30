#!/usr/bin/env ruby

# Ruby Test File for TLDR Formatter Function Detection
# =================================================
# This file tests whether the TLDR formatter correctly distinguishes between:
# - Function DEFINITIONS (should be detected)
# - Function CALLS (should NOT be detected)

require 'json'
require 'net/http'

# ======================
# FUNCTION DEFINITIONS (SHOULD BE DETECTED)
# ======================

# Basic method definitions
def hello_world
  puts "Hello, World!"
end

def add_numbers(a, b)
  a + b
end

def calculate_area(width, height)
  width * height
end

# Method with default parameters
def greet_user(name, greeting = "Hello")
  puts "#{greeting}, #{name}!"
end

# Method with keyword arguments
def create_person(name:, age:, email: nil)
  {
    name: name,
    age: age,
    email: email
  }
end

# Method with splat operators
def sum_all(*numbers)
  numbers.reduce(0, :+)
end

def process_options(**options)
  options.each { |key, value| puts "#{key}: #{value}" }
end

# Predicate methods (ending with ?)
def valid_email?(email)
  email.include?('@')
end

def empty_array?(arr)
  arr.nil? || arr.empty?
end

def positive_number?(num)
  num > 0
end

# Mutating methods (ending with !)
def upcase_string!(str)
  str.upcase!
end

def reverse_array!(arr)
  arr.reverse!
end

def sort_hash!(hash)
  hash.sort!
end

# Methods with blocks
def each_with_index_custom(array, &block)
  array.each_with_index(&block)
end

def timing_wrapper
  start_time = Time.now
  result = yield
  puts "Execution time: #{Time.now - start_time}"
  result
end

def fibonacci_generator(limit)
  a, b = 0, 1
  while a < limit
    yield a
    a, b = b, a + b
  end
end

# Class definitions with methods
class Person
  attr_reader :name, :age
  attr_writer :email
  attr_accessor :phone
  
  # Class methods
  def self.create_anonymous
    new("Anonymous", 0)
  end
  
  def self.total_population
    @@population || 0
  end
  
  def self.validate_age(age)
    age.is_a?(Integer) && age >= 0
  end
  
  # Constructor
  def initialize(name, age)
    @name = name
    @age = age
  end
  
  # Instance methods
  def to_s
    "#{@name} (#{@age} years old)"
  end
  
  def inspect
    "#<Person:#{object_id} @name=#{@name.inspect}>"
  end
  
  def greet
    "Hello, I'm #{@name}"
  end
  
  def celebrate_birthday!
    @age += 1
  end
  
  def adult?
    @age >= 18
  end
  
  def same_age_as?(other)
    @age == other.age
  end
  
  # Private methods
  private
  
  def validate_name(name)
    !name.nil? && !name.empty?
  end
  
  def format_phone(phone)
    phone.gsub(/[^0-9]/, '')
  end
  
  # Protected methods
  protected
  
  def compare_ages(other)
    @age <=> other.age
  end
end

# Module definitions
module StringUtils
  def capitalize_words(str)
    str.split.map(&:capitalize).join(' ')
  end
  
  def remove_spaces(str)
    str.gsub(/\s+/, '')
  end
  
  def self.default_separator
    "-"
  end
  
  module_function :capitalize_words, :remove_spaces
end

module Enumerable
  def average
    return 0 if empty?
    sum.to_f / size
  end
  
  def median
    sorted = sort
    len = sorted.length
    len.odd? ? sorted[len / 2] : (sorted[len / 2 - 1] + sorted[len / 2]) / 2.0
  end
end

# Class with inheritance
class Student < Person
  include StringUtils
  
  def initialize(name, age, student_id)
    super(name, age)
    @student_id = student_id
  end
  
  def study_subject(subject)
    puts "#{@name} is studying #{subject}"
  end
  
  def to_s
    "Student: #{super} (ID: #{@student_id})"
  end
  
  def self.create_with_id(name, age, id)
    new(name, age, id)
  end
end

# Singleton methods
class MathUtils
  def self.square(n)
    n * n
  end
  
  def self.cube(n)
    n * n * n
  end
  
  def self.factorial(n)
    return 1 if n <= 1
    n * factorial(n - 1)
  end
end

# Metaprogramming methods
class DynamicMethods
  def self.define_getter(attr_name)
    define_method(attr_name) do
      instance_variable_get("@#{attr_name}")
    end
  end
  
  def self.define_setter(attr_name)
    define_method("#{attr_name}=") do |value|
      instance_variable_set("@#{attr_name}", value)
    end
  end
  
  def method_missing(method_name, *args, &block)
    if method_name.to_s.start_with?('get_')
      attr_name = method_name.to_s[4..-1]
      instance_variable_get("@#{attr_name}")
    else
      super
    end
  end
  
  def respond_to_missing?(method_name, include_private = false)
    method_name.to_s.start_with?('get_') || super
  end
end

# Lambda and Proc creation methods
def create_multiplier(factor)
  lambda { |x| x * factor }
end

def create_adder(increment)
  proc { |x| x + increment }
end

def with_custom_block(&block)
  block.call("test") if block_given?
end

# Operator overloading
class Vector
  def initialize(x, y)
    @x, @y = x, y
  end
  
  def +(other)
    Vector.new(@x + other.x, @y + other.y)
  end
  
  def -(other)
    Vector.new(@x - other.x, @y - other.y)
  end
  
  def *(scalar)
    Vector.new(@x * scalar, @y * scalar)
  end
  
  def ==(other)
    @x == other.x && @y == other.y
  end
  
  def <=>(other)
    magnitude <=> other.magnitude
  end
  
  def [](index)
    case index
    when 0 then @x
    when 1 then @y
    end
  end
  
  def []=(index, value)
    case index
    when 0 then @x = value
    when 1 then @y = value
    end
  end
  
  def magnitude
    Math.sqrt(@x * @x + @y * @y)
  end
end

# Exception handling methods
class CustomError < StandardError
  def initialize(message, code = nil)
    super(message)
    @code = code
  end
  
  def to_s
    @code ? "#{super} (Code: #{@code})" : super
  end
end

def validate_input(input)
  raise ArgumentError, "Input cannot be nil" if input.nil?
  raise CustomError.new("Invalid input", 1001) if input.empty?
  true
end

def safe_divide(a, b)
  raise ArgumentError, "Division by zero" if b == 0
  a.to_f / b
rescue ArgumentError => e
  puts "Error: #{e.message}"
  nil
end

# File handling methods
def read_config_file(filename)
  File.open(filename, 'r') do |file|
    JSON.parse(file.read)
  end
rescue IOError => e
  puts "Error reading file: #{e.message}"
  {}
end

def write_log_entry(message)
  File.open('app.log', 'a') do |file|
    file.puts "#{Time.now}: #{message}"
  end
end

# ======================
# FUNCTION CALLS (SHOULD NOT BE DETECTED)
# ======================

# These are method calls, not definitions - they should NOT be detected

# Built-in method calls
puts "Starting application..."
print "Enter your name: "
p "Debug message"

# String method calls
name = "John Doe"
name.upcase
name.downcase
name.strip
name.length
name.empty?
name.include?("John")
name.gsub("John", "Jane")
name.split(" ")

# Array method calls
numbers = [1, 2, 3, 4, 5]
numbers.each { |n| puts n }
numbers.map { |n| n * 2 }
numbers.select { |n| n.even? }
numbers.reject { |n| n.odd? }
numbers.reduce(0) { |sum, n| sum + n }
numbers.find { |n| n > 3 }
numbers.sort
numbers.reverse
numbers.push(6)
numbers.pop
numbers.shift
numbers.unshift(0)
numbers.first
numbers.last
numbers.length
numbers.size
numbers.empty?
numbers.include?(3)

# Hash method calls
config = { host: 'localhost', port: 3000 }
config.keys
config.values
config.each { |k, v| puts "#{k}: #{v}" }
config.merge({ ssl: true })
config.has_key?(:host)
config.fetch(:port, 8080)
config.delete(:ssl)

# File method calls
File.exist?("config.json")
File.read("data.txt")
File.write("output.txt", "content")
File.delete("temp.txt")
File.size("large_file.dat")
File.directory?("uploads")

# Dir method calls
Dir.entries(".")
Dir.glob("*.rb")
Dir.mkdir("new_folder")
Dir.chdir("/tmp")
Dir.pwd

# Time method calls
Time.now
Time.parse("2023-01-01")
Time.at(1640995200)

# Math method calls
Math.sqrt(16)
Math.sin(Math::PI / 2)
Math.cos(0)
Math.log(Math::E)
Math.abs(-5)

# JSON method calls
json_data = '{"name": "John", "age": 30}'
JSON.parse(json_data)
JSON.generate({ name: "Jane", age: 25 })

# Net::HTTP method calls
uri = URI("https://api.example.com/data")
Net::HTTP.get(uri)
Net::HTTP.post_form(uri, { key: "value" })

# Enumerable method calls on arrays
[1, 2, 3].map(&:to_s)
[1, 2, 3].select(&:odd?)
[1, 2, 3].reject(&:even?)
[1, 2, 3].find(&:positive?)
[1, 2, 3].all?(&:positive?)
[1, 2, 3].any?(&:negative?)
[1, 2, 3].none?(&:zero?)

# String interpolation and method calls
age = 25
puts "I am #{age} years old"
puts "Next year I'll be #{age + 1}"
puts "Age doubled: #{age * 2}"

# Class method calls
Person.create_anonymous
Person.total_population
Person.validate_age(30)
MathUtils.square(5)
MathUtils.cube(3)
MathUtils.factorial(4)
Student.create_with_id("Alice", 20, "ST001")

# Instance method calls
person = Person.new("Bob", 25)
person.greet
person.celebrate_birthday!
person.adult?
person.to_s
person.inspect

student = Student.new("Charlie", 19, "ST002")
student.study_subject("Mathematics")
student.same_age_as?(person)

# Module method calls
StringUtils.capitalize_words("hello world")
StringUtils.remove_spaces("a b c")
StringUtils.default_separator

# Proc and Lambda calls
multiplier = create_multiplier(3)
multiplier.call(5)

adder = create_adder(10)
adder.call(5)

# Block calls
[1, 2, 3].each do |num|
  puts num
end

numbers.map do |n|
  n * 2
end

# Exception handling with method calls
begin
  validate_input("")
rescue CustomError => e
  puts e.message
end

begin
  safe_divide(10, 0)
rescue => e
  puts "Unexpected error: #{e.message}"
end

# File operations with method calls
config_data = read_config_file("config.json")
write_log_entry("Application started")

# Chained method calls
"  Hello World  ".strip.upcase.reverse
[1, 2, 3, 4, 5].select(&:odd?).map(&:to_s).join(", ")

# Method calls with blocks
fibonacci_generator(20) do |num|
  puts num
end

timing_wrapper do
  sleep(0.1)
  "Task completed"
end

# Range method calls
(1..10).each { |i| puts i }
(1...10).to_a
(1..10).include?(5)
(1..10).cover?(5)

# Regex method calls
pattern = /\d+/
"abc123def".match(pattern)
"abc123def".scan(pattern)
"abc123def".gsub(pattern, "XXX")

# Method calls on objects
vector1 = Vector.new(1, 2)
vector2 = Vector.new(3, 4)
result = vector1 + vector2
result.magnitude

# Conditional method calls
puts "Adult" if person.adult?
puts "Valid" if valid_email?("test@example.com")
puts "Empty" if empty_array?([])

# Method calls in assignments
sum = add_numbers(5, 3)
area = calculate_area(10, 20)
greeting = greet_user("Alice", "Hi")

# Method calls with different argument styles
person_data = create_person(name: "David", age: 35, email: "david@example.com")
total = sum_all(1, 2, 3, 4, 5)
process_options(host: "localhost", port: 3000, ssl: true)

# ======================
# ATTRIBUTE ACCESSORS (SHOULD BE DETECTED)
# ======================

# These create getter/setter methods and should be detected
class Product
  attr_reader :name, :price
  attr_writer :description
  attr_accessor :category, :stock_quantity
end

class Order
  attr_reader :id, :customer_id, :total
  attr_writer :status
  attr_accessor :items, :shipping_address
end

# ======================
# ALIAS METHODS (SHOULD BE DETECTED)
# ======================

# Method aliases create new method names and should be detected
class Calculator
  def add(a, b)
    a + b
  end
  
  def subtract(a, b)
    a - b
  end
  
  # These create new method definitions
  alias plus add
  alias minus subtract
  alias_method :sum, :add
  alias_method :difference, :subtract
end

# ======================
# SCOPE MODIFIERS (AFFECT VISIBILITY BUT DON'T CREATE METHODS)
# ======================

class TestClass
  def public_method
    "I'm public"
  end
  
  private
  
  def private_method
    "I'm private"
  end
  
  protected
  
  def protected_method
    "I'm protected"
  end
  
  public
  
  def another_public_method
    "I'm also public"
  end
end

# ======================
# SUMMARY
# ======================

# Expected DETECTIONS (method definitions):
# - hello_world, add_numbers, calculate_area
# - greet_user, create_person, sum_all, process_options
# - valid_email?, empty_array?, positive_number?
# - upcase_string!, reverse_array!, sort_hash!
# - each_with_index_custom, timing_wrapper, fibonacci_generator
# - Person class methods: create_anonymous, total_population, validate_age
# - Person instance methods: initialize, to_s, inspect, greet, celebrate_birthday!, adult?, same_age_as?, validate_name, format_phone, compare_ages
# - StringUtils module methods: capitalize_words, remove_spaces, default_separator
# - Enumerable methods: average, median
# - Student methods: initialize, study_subject, to_s, create_with_id
# - MathUtils methods: square, cube, factorial
# - DynamicMethods methods: define_getter, define_setter, method_missing, respond_to_missing?
# - Lambda/Proc methods: create_multiplier, create_adder, with_custom_block
# - Vector methods: initialize, +, -, *, ==, <=>, [], []=, magnitude
# - Exception methods: initialize, to_s, validate_input, safe_divide
# - File methods: read_config_file, write_log_entry
# - attr_reader, attr_writer, attr_accessor (creates getter/setter methods)
# - alias and alias_method (creates new method definitions)
# - TestClass methods: public_method, private_method, protected_method, another_public_method

# Expected NON-DETECTIONS (method calls):
# - puts, print, p calls
# - String method calls: upcase, downcase, strip, length, empty?, include?, gsub, split
# - Array method calls: each, map, select, reject, reduce, find, sort, reverse, push, pop, etc.
# - Hash method calls: keys, values, each, merge, has_key?, fetch, delete
# - File method calls: exist?, read, write, delete, size, directory?
# - Dir method calls: entries, glob, mkdir, chdir, pwd
# - Time method calls: now, parse, at
# - Math method calls: sqrt, sin, cos, log, abs
# - JSON method calls: parse, generate
# - Net::HTTP method calls: get, post_form
# - All instance method calls on objects
# - All chained method calls
# - All method calls in blocks
# - All method calls in conditionals and assignments