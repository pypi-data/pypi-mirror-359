# Only 1 method definition - should detect only this
def real_method
  # Many method calls below - should NOT be detected
  puts "test"
  print "hello"
  p "debug"
  "string".upcase
  "string".downcase
  "string".strip
  "string".length
  [1, 2, 3].each { |n| puts n }
  [1, 2, 3].map { |n| n * 2 }
  [1, 2, 3].select { |n| n > 1 }
  {a: 1, b: 2}.keys
  {a: 1, b: 2}.values
  File.exist?("file.txt")
  File.read("file.txt")
  Time.now
  Math.sqrt(16)
  JSON.parse("{}")
end

# Method calls that should NOT be detected
real_method()
puts "output"
print "more output"
p "debug output"
"test".upcase
[1, 2, 3].each { |n| puts n }