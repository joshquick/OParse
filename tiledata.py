import sys
import os
import struct
import xml.etree.ElementTree as ET

metric = {100:'Cluster density', 101:'Cluster density Pf', 102:'Clusters', 103:'Clusters Pf', 200:'Phasing R1', 201:'Prephasing R1', 202:'Phasing R2', 203:'Prephasing R2', 300:'Percent aligned R1', 301:'Percent aligned R2', 400:'Unknown'}

codes = sorted(metric.keys())

def parse_tile_metrics(f):
    #get the run id
    tree = ET.parse(f + '/RunInfo.xml')
    root = tree.getroot()
    run_id = root[0].attrib['Id']
    print 'Parsing tile data for run id', run_id
    
    #read the header and file length
    try:
    	file = open(f + '/InterOp/TileMetricsOut.bin', 'r')
    except IOError:
    	print f + '/InterOp/TileMetricsOut.bin not found...'
    	sys.exit()

    print 'File version', struct.unpack('B', file.read(1))[0]
    record_size = struct.unpack('B', file.read(1))[0]
    file.seek(0, 2)
    length = file.tell() - 2
    file.seek(2, 0)

    i = 0
    data = []
    while True:
    	data.append((struct.unpack('HHH', file.read(6))) + (struct.unpack('f', file.read(4))))
    	i += 10
    	if i == length:
    		break
    lanes = sorted(set([record[0] for record in data]))
    tiles = sorted(set([record[1] for record in data]))

    output_dir = f + '/InterOp/Text/'
    output_path = f + '/InterOp/Text/TileMetricsOut.txt'
    if not os.path.exists(output_dir):
    	os.makedirs(output_dir)
    with open(output_path, 'w') as outfile:
    	print >>outfile, ','.join(['Run Id', 'Lane', 'Tile'] + [metric[code] for code in codes])
    	for lane in lanes:
    		for tile in tiles:
    			a = [run_id, lane, tile]
    			for code in codes:
    				t = [record[3] for record in data if record[0] == lane and record[1] == tile and record[2] == code]
    				if t:
    					a.append(t[-1])
    				else:
    					a.append('')
    			print >>outfile, '%s,%i,%i,%.3f,%.3f,%.3f,%.3f,%.6f,%.6f,%.6f,%.6f,%.6f,%s,%.6f' %tuple(a)
                
if __name__ == '__main__':
    parse_tile_metrics(sys.argv[1])               