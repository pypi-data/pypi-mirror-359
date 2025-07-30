# SHOULD BE DETECTED - Method definitions
def simple_method
  puts "test"  # Should NOT be detected - method call
  return "result"
end

def method_with_params(param1, param2)
  puts param1  # Should NOT be detected - method call
  return param1 + param2
end

class TestClass
  def instance_method
    puts "instance"  # Should NOT be detected - method call
  end
  
  def self.class_method
    puts "class"  # Should NOT be detected - method call
  end
end

# SHOULD NOT BE DETECTED - Method calls
simple_method()
method_with_params(1, 2)
puts "hello"
print "world"
p "debug"

obj = TestClass.new
obj.instance_method
TestClass.class_method

# More method calls that should NOT be detected
"hello".upcase
[1, 2, 3].each { |n| puts n }
{a: 1, b: 2}.keys
File.exist?("test.txt")
Time.now