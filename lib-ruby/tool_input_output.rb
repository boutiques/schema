#
# Copyright (C) 2015
# The Royal Institution for the Advancement of Learning
# McGill University
#    and
# Centre National de la Recherche Scientifique 
# CNRS
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 
#
#
# Meta-class for tool Inputs and Outputs
class ToolInputOutput
  def initialize name,type,syntax_key,documentation,cardinality 
    @name = name               # the name of the input/output. Should be usable as a Ruby variable name
    raise "Unknown input/output type: #{type}" unless type == "String" or type == "File"
    raise "Unsupported cardinality" if cardinality != "Single" and cardinality != "Multiple"
    @cardinality = cardinality
    @type = type               # might be "String" of "File"
    @syntax_key = syntax_key   # a placeholder where the
                               # value of this input or output
                               # will be replaced on the command line.
    @documentation = documentation
  end
  def get_name
    return @name
  end
  def get_type
    return @type
  end
  def get_syntax_key
    return @syntax_key
  end
  def get_documentation
    return @documentation
  end
  def get_cardinality
    return @cardinality
  end
  def to_json
    output = "{ 
      \"name\" : \"#{@name}\",
      \"type\" : \"#{@type}\",
      \"description\" : \"#{@documentation}\",
      \"command-line-key\" : \"#{@syntax_key}\",
      \"cardinality\" : \"#{@cardinality}\"
    }"
    return output
  end
end
