class TestClass
  # These create getter/setter methods and should potentially be detected
  attr_reader :name
  attr_writer :age  
  attr_accessor :email
  
  def initialize(name)
    @name = name
  end
  
  def greet
    puts "Hello, #{@name}"
  end
  
  # These create new method definitions and should potentially be detected
  alias old_greet greet
  alias_method :say_hello, :greet
end