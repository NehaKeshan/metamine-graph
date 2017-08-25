import urllib2
import csv
import sys

kb=":"
out_fn = "out.ttl"
prefix_fn="prefixes.txt"

studyRef = None

# Need to implement input flags rather than ordering
if (len(sys.argv) < 2) :
    print "Usage: python sdd2owl.py <SDD_file> [<data_file>] [<codebook_file>] [<output_file>] [kb_prefix]\nOptional arguments can be skipped by entering '!'"
    sys.exit(1)

if (len(sys.argv) > 1) :
    sdd_fn = sys.argv[1]

    if (len(sys.argv) > 2) :
        data_fn = sys.argv[2]

        if (len(sys.argv) > 3) :
            cb_fn = sys.argv[3]
            if (len(sys.argv) > 4) :
                out_fn = sys.argv[4]
                if (len(sys.argv) > 5) :
                    if not (sys.argv[5] == "!" ):
                        if ":" not in sys.argv[5] :
                            kb = sys.argv[5] + ":"
                        else :                       
                            kb = sys.argv[5]
        else :
            cb_fn = raw_input("If you wish to use a Codebook file, please type the path and press 'Enter'.\n Otherwise, type '!' and press Enter: ")       
    else : 
        data_fn = raw_input("If you wish to use a Data file, please type the path and press 'Enter'.\n Otherwise, type '!' and press Enter: ")
        cb_fn = raw_input("If you wish to use a Codebook file, please type the path and press 'Enter'.\n Otherwise, type '!' and press Enter: ")

if cb_fn == "!" :
    cb_fn = None

if data_fn == "!" :
    data_fn = None

if out_fn == "!" :
    out_fn = "out.ttl"

output_file = open(out_fn,"w")
prefix_file = open(prefix_fn,"r")
prefixes = prefix_file.readlines()

for prefix in prefixes :
    output_file.write(prefix)
output_file.write("\n")

code_mappings_url = 'https://raw.githubusercontent.com/tetherless-world/chear-ontology/master/code_mappings.csv'
code_mappings_response = urllib2.urlopen(code_mappings_url)
code_mappings_reader = csv.reader(code_mappings_response)

column_ind = None
attr_ind = None
attr_of_ind = None
entity_ind = None
unit_ind = None
time_ind = None
role_ind = None
relation_ind = None
relation_to_ind = None
derived_from_ind = None
generated_by_ind = None
position_ind = None
label_ind = None
comment_ind = None

sdd_key = None
cb_key = None
data_key = None

unit_code_list = []
unit_uri_list = []
unit_label_list = []

actual_list = []
virtual_list = []

actual_tuples = []
virtual_tuples = []
cb_tuple = {}

try :
    sdd_file = open(sdd_fn, 'r')
except:
    print "Error: The specified SDD file does not exist."
    sys.exit(1)

try: 
    row_num=0
    sdd_reader=csv.reader(sdd_file)
    # Set virtual and actual columns
    for row in sdd_reader :
        if row_num==0:
            sdd_key = row
        else :
            try :
                column_ind = sdd_key.index("Column")
                if row[column_ind].startswith("??") :
                    virtual_list.append(row)
                else :
                    actual_list.append(row)
            except:
                print "Error: The SDD must have a column named 'Column'"
                sys.exit(1)
        row_num += 1
except : 
    print "Something went wrong when trying to read the SDD"
    sys.exit(1)

for code_row in code_mappings_reader :
    unit_code_list.append(code_row[0])
    unit_uri_list.append(code_row[1])
    unit_label_list.append(code_row[2])

# Remove list labels
del unit_code_list[0]
del unit_uri_list[0] 
del unit_label_list[0]

def codeMapper(input_word) :
    unitVal = input_word
    for unit_label in unit_label_list :
        if (unit_label == input_word) :
            unit_index = unit_label_list.index(unit_label)
            unitVal = unit_uri_list[unit_index]
    for unit_code in unit_code_list :
        if (unit_code == input_word) :
            unit_index = unit_code_list.index(unit_code)
            unitVal = unit_uri_list[unit_index]
    return unitVal    

def convertVirtualToKGEntry(*args) :
    if (args[0][:2] == "??") :
        if (studyRef is not None ) :
            if (args[0]==studyRef) :
                return kb + args[0][2:]
        if (len(args) == 2) :
            return kb + args[0][2:] + "-" + args[1]
        else : 
            return kb + args[0][2:]
    elif (':' not in args[0]) :
        # Need to implement check for entry in column list
        return '"' + args[0] + "\"^^xsd:string"
    else :
        return args[0]

def checkVirtual(input_word) :
    if (input_word[:2] == "??") :
        return True
    else :
        return False


# Set indices
try :
    attr_ind = sdd_key.index("Attribute")
except :
    print "Error: The SDD must have a column named 'Attribute'"
    sys.exit(1)

try :
    attr_of_ind = sdd_key.index("attributeOf")
except :
    print "Error: The SDD must have a column named 'attributeOf'"
    sys.exit(1)

try :
    entity_ind = sdd_key.index("Entity")
except :
    print "Error: The SDD must have a column named 'Entity'"
    sys.exit(1)

try :
    unit_ind = sdd_key.index("Unit")
except :
    print "Error: The SDD must have a column named 'Unit'"
    sys.exit(1)

try :
    time_ind = sdd_key.index("Time")
except :
    print "Warning: Optional SDD column 'Time' is missing"

try :
    role_ind = sdd_key.index("Role")
except :
    print "Error: The SDD must have a column named 'Role'"
    sys.exit(1)

try:
    relation_ind = sdd_key.index("Relation")
except :
    print "Error: The SDD must have a column named 'Relation'"
    sys.exit(1)

try :
    relation_to_ind = sdd_key.index("inRelationTo")
except :
    print "Error: The SDD must have a column named 'inRelationTo'"
    sys.exit(1)

try:
    derived_from_ind = sdd_key.index("wasDerivedFrom")
except :
    print "Warning: Optional SDD column 'wasDerivedFrom' is missing"

try:
    generated_by_ind = sdd_key.index("wasGeneratedBy")
except :
    print "Warning: Optional SDD column 'wasGeneratedBy' is missing"

try:
    position_ind = sdd_key.index("hasPosition")    
except :
    print "Warning: Optional SDD column 'hasPosition' is missing"

try:
    label_ind = sdd_key.index("Label")    
except :
    print "Warning: Optional SDD column 'Label' is missing"

try:
    comment_ind = sdd_key.index("Comment")    
except :
    print "Warning: Optional SDD column 'Comment' is missing"

def writeVirtualRDF(virtual_list, virtual_tuples, output_file) :
    for item in virtual_list :
        virtual_tuple = {}
        output_file.write(kb + item[column_ind][2:] + " a owl:Class ")
        output_file.write(" ;\n\trdfs:label \"" + item[column_ind][2:] + "\"")
        # Set the rdf:type of the virtual row to either the Attribute or Entity value (or else owl:Individual)
        if (item[entity_ind] != "") and (item[attr_ind] == "") :
            output_file.write(" ;\n\trdfs:subClassOf " + codeMapper(item[entity_ind]))
            virtual_tuple["Column"]=item[column_ind]
            virtual_tuple["Entity"]=codeMapper(item[entity_ind])
            if (virtual_tuple["Entity"] == "hasco:Study") :
                global studyRef
                studyRef = item[column_ind]
                virtual_tuple["Study"] = item[column_ind]
        elif (item[entity_ind] == "") and (item[attr_ind] != "") :
            output_file.write(" ;\n\trdfs:subClassOf " + codeMapper(item[attr_ind]))
            virtual_tuple["Column"]=item[column_ind]
            virtual_tuple["Attribute"]=codeMapper(item[attr_ind])
        else :
            print "Warning: Virtual column not assigned an Entity or Attribute value, or was assigned both."
            virtual_tuple["Column"]=item[column_ind]
        
        # If there is a value in the inRelationTo column ...
        if (item[relation_to_ind] != "") :
            virtual_tuple["inRelationTo"]=item[relation_to_ind]
            # If there is a value in the Relation column but not the Role column ...
            if (item[relation_ind] != "") and (item[role_ind] == "") :
                output_file.write(" ;\n\t" + item[relation_ind] + " " + convertVirtualToKGEntry(item[relation_to_ind]) )
                virtual_tuple["Relation"]=item[relation_ind]
            # If there is a value in the Role column but not the Relation column ...
            elif (item[relation_ind] == "") and (item[role_ind] != "") :
                output_file.write(" ;\n\tsio:hasRole [ a " + item[role_ind] + " ;\n\t\tsio:inRelationTo " + convertVirtualToKGEntry(item[relation_to_ind]) + " ]")
                virtual_tuple["Role"]=item[role_ind]
            # If there is a value in the Role and Relation columns ...
            elif (item[relation_ind] != "") and (item[role_ind] != "") :
                virtual_tuple["Relation"]=item[relation_ind]
                virtual_tuple["Role"]=item[role_ind]
        if (derived_from_ind is not None) and (item[derived_from_ind] != "") :
            output_file.write(" ;\n\tprov:wasDerivedFrom " + convertVirtualToKGEntry(item[derived_from_ind]))
            virtual_tuple["wasDerivedFrom"]=item[derived_from_ind]
        if (generated_by_ind is not None) and (item[generated_by_ind] != "") :
            output_file.write(" ;\n\tprov:wasGeneratedBy " + convertVirtualToKGEntry(item[generated_by_ind]))
            virtual_tuple["wasGeneratedBy"]=item[generated_by_ind]        
        output_file.write(" .\n\n")
        virtual_tuples.append(virtual_tuple)

def writeActualRDF(actual_list, actual_tuples, output_file) :
    for item in actual_list :
        actual_tuple = {}
        output_file.write(kb + item[column_ind] + " a owl:Class ")
        output_file.write(" ;\n\trdfs:label \"" + item[column_ind] + "\"")
        if (item[attr_ind] != "") :
            output_file.write(" ;\n\trdfs:subClassOf " + convertVirtualToKGEntry(codeMapper(item[attr_ind])))
            actual_tuple["Column"]=item[column_ind]
            actual_tuple["Attribute"]=codeMapper(item[attr_ind])
        else :
            print "Error: Actual column not assigned an Attribute value."
            sys.exit(1)
            #output_file.write(kb + item[column_ind] + " a owl:Individual")
        if (item[attr_of_ind] != "") :
            output_file.write(" ;\n\tsio:isAttributeOf " + convertVirtualToKGEntry(item[attr_of_ind]))
            actual_tuple["isAttributeOf"]=item[attr_of_ind]
        else :
            print "Error: Actual column not assigned an isAttributeOf value."
            sys.exit(1)
        if (item[unit_ind] != "") :
            output_file.write(" ;\n\tsio:hasUnit " + codeMapper(item[unit_ind]))
            actual_tuple["Unit"] = codeMapper(item[unit_ind])
        if (derived_from_ind is not None) and (item[derived_from_ind] != "") :
            output_file.write(" ;\n\tprov:wasDerivedFrom " + convertVirtualToKGEntry(item[derived_from_ind]))
            actual_tuple["wasDerivedFrom"]=item[derived_from_ind]
        if (generated_by_ind is not None) and (item[generated_by_ind] != "") :
            output_file.write(" ;\n\tprov:wasGeneratedBy " + convertVirtualToKGEntry(item[generated_by_ind]))
            actual_tuple["wasGeneratedBy"]=item[generated_by_ind]
        if (position_ind is not None) and (item[position_ind] != "") :
            output_file.write(" ;\n\thasco:hasPosition \"" + item[position_ind] + "\"^^xsd:Integer")
            actual_tuple["hasPosition"]=item[position_ind]
        if (time_ind is not None) and (item[time_ind] != "") :
            output_file.write(" ;\n\tsio:existsAt " + convertVirtualToKGEntry(item[time_ind]))
            actual_tuple["Time"]=item[time_ind]
        if (relation_to_ind is not None) and (item[relation_to_ind] != "") :
            output_file.write(" ;\n\tsio:inRelationTo " + convertVirtualToKGEntry(item[relation_to_ind]))
            actual_tuple["inRelationTo"]=item[relation_to_ind]
        if (relation_ind is not None) and (item[relation_ind] != "") :
            output_file.write(" ;\n\t" + item[relation_ind] + " " + convertVirtualToKGEntry(item[relation_to_ind]))
            actual_tuple["Relation"]=item[relation_ind]
        if (label_ind is not None) and (item[label_ind] != "") :
            output_file.write(" ;\n\trdfs:label \"" + item[label_ind] + "\"^^xsd:String" )
            actual_tuple["Label"]=item[label_ind]
        if (comment_ind is not None) and (item[comment_ind] != "") :
            output_file.write(" ;\n\trdfs:comment \"" + item[comment_ind] + "\"^^xsd:String")
            actual_tuple["Comment"]=item[comment_ind]
        output_file.write(" .\n\n")
        actual_tuples.append(actual_tuple)

writeVirtualRDF(virtual_list, virtual_tuples, output_file)
writeActualRDF(actual_list, actual_tuples, output_file)

if cb_fn is not None :
    cb_column_ind = None
    cb_code_ind = None
    cb_label_ind = None
    cb_class_ind = None
    try :
        cb_file = open(cb_fn, 'r')
    except :
        print "Error: The specified Codebook file does not exist."
        sys.exit(1)
    try :
        row_num=0
        cb_reader=csv.reader(cb_file)
        inner_tuple_list = []
        for row in cb_reader :
            if row_num == 0:
                cb_key = row
                try :
                    cb_column_ind = cb_key.index("Column")
                except :
                    print "Error: The Codebook must have a column named 'Column'"
                    sys.exit(1)
                try :
                    cb_code_ind = cb_key.index("Code")
                except :
                    print "Error: The Codebook must have a column named 'Code'"
                    sys.exit(1)
                try :
                    cb_label_ind = cb_key.index("Label")
                except :
                    print "Error: The Codebook must have a column named 'Label'"
                    sys.exit(1)
                try :
                    cb_class_ind = cb_key.index("Class")
                except :
                    print "Warning: The Codebook is missing an optional column named 'Class'"
            else :
                if (row[cb_column_ind] not in cb_tuple) :
                    inner_tuple_list=[]
                inner_tuple = {}
                inner_tuple["Code"]=row[cb_code_ind]
                inner_tuple["Label"]=row[cb_label_ind]
                if(cb_class_ind is not None) :
                    inner_tuple["Class"]=row[cb_class_ind]
                inner_tuple_list.append(inner_tuple)
                cb_tuple[row[cb_column_ind]]=inner_tuple_list
            row_num += 1
    except :
        print "Warning: Unable to process Codebook file"

def convertFromCB(dataVal,column_name) :
    if column_name in cb_tuple :
        for tuple_row in cb_tuple[column_name] :
            if (tuple_row['Code'].__str__() is dataVal.__str__()) :
                if "Class" in tuple_row :
                    return tuple_row['Class']     
                else :
                    return "\"" + tuple_row['Label'] + "\"^^xsd:String"
        return dataVal
    else :
        return dataVal

def writeVirtualEntry(output_file, v_column, index) : 
    try :
        for v_tuple in virtual_tuples :
            if (v_tuple["Column"] == v_column) :
                if "Study" in v_tuple :
                    continue
                else :
                    output_file.write(kb + v_tuple["Column"][2:] + "-" + index + " a " + kb + v_tuple["Column"][2:])
                if "Entity" in v_tuple :
                    output_file.write(";\n\ta " + v_tuple["Entity"])
                if "Attribute" in v_tuple :
                    output_file.write(";\n\ta " + v_tuple["Attribute"])
                if "Subject" in v_tuple :
                    output_file.write(";\n\tsio:hasIdentifier " + kb + v_tuple["Subject"] + "-" + index)
                if "inRelationTo" in v_tuple :
                    if ("Role" in v_tuple) and ("Relation" not in v_tuple) :
                        output_file.write(" ;\n\tsio:hasRole [ a " + v_tuple["Role"] + " ;\n\t\tsio:inRelationTo " + convertVirtualToKGEntry(v_tuple["inRelationTo"], index) + " ]")
                    elif ("Role" not in v_tuple) and ("Relation" in v_tuple) :
                        output_file.write(" ;\n\t" + v_tuple["Relation"] + " " + convertVirtualToKGEntry(v_tuple["inRelationTo"],index))
                if "wasGeneratedBy" in v_tuple : 
                    output_file.write(" ;\n\tprov:wasGeneratedBy " + convertVirtualToKGEntry(v_tuple["wasGeneratedBy"],index))
                if "wasDerivedFrom" in v_tuple : 
                    output_file.write(" ;\n\tprov:wasDerivedFrom " + convertVirtualToKGEntry(v_tuple["wasDerivedFrom"],index))
                #output_file.write(";\n\tprov:wasDerivedFrom " + kb + v_tuple["Column"][2:])
                output_file.write(" .\n\n")
                if ("wasGeneratedBy" in v_tuple ) and (checkVirtual(v_tuple["wasGeneratedBy"])) :
                    writeVirtualEntry(output_file, v_tuple["wasGeneratedBy"], index)
                if ("wasDerivedFrom" in v_tuple) and (checkVirtual(v_tuple["wasDerivedFrom"])) :
                    writeVirtualEntry(output_file, v_tuple["wasDerivedFrom"], index)
    except :
        print "Warning: Unable to create virtual entry."

if data_fn is not None :
    try :
        data_file = open(data_fn, 'r')
    except :
        print "Error: The specified Data file does not exist."
        sys.exit(1)
    try :
        row_num=0
        id_index=None
        data_reader=csv.reader(data_file)
        for row in data_reader :
            if row_num==0:
                try :
                    data_key = row
                    #print row
                    for item in row :
                        for a_tuple in actual_tuples :
                            if item == a_tuple["Column"] :
                                if (a_tuple["Attribute"] == "hasco:originalID") or (a_tuple["Attribute"] == "sio:Identifier") :
                                    #print "Found ID"
                                    id_index = row.index(item)
                                    for v_tuple in virtual_tuples :
                                        if (a_tuple["isAttributeOf"] == v_tuple["Column"]) :
                                            v_tuple["Subject"]=a_tuple["Column"]
                                            #print v_tuple
                    if (id_index is None) :
                        print "Error: To process Data it is necessary to have a \"hasco:originalID\" or \"sio:Identifier\" Attribute in the SDD."
                        sys.exit(1)
                except:
                    print "Warning: Something went wrong on the first Data row."
            else:
                try :
                    vref_list = []
                    for a_tuple in actual_tuples :
                        if (a_tuple["Column"] in data_key ) :
                            try :
                                output_file.write(kb + a_tuple["Column"] + "-" + row[id_index] + " a " + a_tuple["Attribute"])
                                output_file.write(" ;\n\ta " + kb + a_tuple["Column"])
                                output_file.write(" ;\n\tsio:isAttributeOf " + convertVirtualToKGEntry(a_tuple["isAttributeOf"],row[id_index]))
                                if checkVirtual(a_tuple["isAttributeOf"]) :
                                    if a_tuple["isAttributeOf"] not in vref_list :
                                        vref_list.append(a_tuple["isAttributeOf"])
                                if "Unit" in a_tuple :
                                    output_file.write(" ;\n\tsio:hasUnit " + a_tuple["Unit"])
                                if "Time" in a_tuple :
                                    output_file.write(" ;\n\tsio:existsAt " + convertVirtualToKGEntry(a_tuple["Time"], row[id_index]))
                                    if checkVirtual(a_tuple["Time"]) :
                                        if a_tuple["Time"] not in vref_list :
                                            vref_list.append(a_tuple["Time"])
                                if "wasDerivedFrom" in a_tuple :
                                    output_file.write(" ;\n\tprov:wasDerivedFrom " + convertVirtualToKGEntry(a_tuple["wasDerivedFrom"], row[id_index]))
                                    if checkVirtual(a_tuple["wasDerivedFrom"]) :
                                        if a_tuple["wasDerivedFrom"] not in vref_list :
                                            vref_list.append(a_tuple["wasDerivedFrom"])
                                if "wasGeneratedBy" in a_tuple :
                                    output_file.write(" ;\n\tprov:wasGeneratedBy " + convertVirtualToKGEntry(a_tuple["wasGeneratedBy"], row[id_index]))
                                    if checkVirtual(a_tuple["wasGeneratedBy"]) :
                                        if a_tuple["wasGeneratedBy"] not in vref_list :
                                            vref_list.append(a_tuple["wasGeneratedBy"])
                                if "inRelationTo" in a_tuple :
                                    if checkVirtual(a_tuple["inRelationTo"]) :
                                        if a_tuple["inRelationTo"] not in vref_list :
                                            vref_list.append(a_tuple["inRelationTo"])
                                    if "Relation" in a_tuple :
                                        output_file.write(" ;\n\t" + a_tuple["Relation"] + " " + convertVirtualToKGEntry(a_tuple["inRelationTo"], row[id_index]))
                                    else :
                                        output_file.write(" ;\n\tsio:inRelationTo " + convertVirtualToKGEntry(a_tuple["inRelationTo"], row[id_index]))
                                if "hasPosition" in a_tuple :
                                    output_file.write(" ;\n\thasco:hasPosition " + a_tuple["hasPosition"])
                                if "Label" in a_tuple :
                                    output_file.write(" ;\n\trdfs:label \"" + a_tuple["Label"] + "\"^^xsd:String")
                                if "Comment" in a_tuple :
                                        output_file.write(" ;\n\trdfs:comment \"" + a_tuple["Comment"] + "\"^^xsd:String")
                                try :
                                    if (row[data_key.index(a_tuple["Column"])] != "") :
                                        #print row[data_key.index(a_tuple["Column"])]
                                        if (cb_fn is not None) :
                                            output_file.write(" ;\n\tsio:hasValue " + convertFromCB(row[data_key.index(a_tuple["Column"])],a_tuple["Column"]))
                                        else :
                                            output_file.write(" ;\n\tsio:hasValue \"" + row[data_key.index(a_tuple["Column"])] + "\"")
                                except :
                                    print "Error writing data value"
                                    print row[data_key.index(a_tuple["Column"])]
                                output_file.write(" .\n\n")
                            except :
                                print "Unable to process tuple" + a_tuple.__str__()
                    #print vref_list
                    for vref in vref_list :
                        writeVirtualEntry(output_file, vref, row[id_index])
                        #print vref
                except:
                    print "Error: Something went wrong when processing actual tuples."
                    sys.exit(1)
            row_num += 1
    except :
        print "Warning: Unable to process Data file"

sdd_file.close()
output_file.close()

if cb_fn is not None :
    cb_file.close()

if data_fn is not None : 
    data_file.close()
