from os import listdir, makedirs
from os.path import exists, isfile, join
import shutil
from PIL import Image
import random
import json
import numpy

debug = False
rng = 256
crng = 255
data = None
unassigned = 0
assigned = 0
scanned = 0

analyze_path = "pixtory-tmp"
# analyze_path = "test"
data_dir = "assets/data"
data_index = ""
load_dir = "assets/data_34.2p"

class BreakIt(Exception): pass

def load():
  global data, assigned, unassigned, scanned
  print "Loading data..."
  files = [f for f in listdir(load_dir) if isfile(join(load_dir, f))]
  if '.DS_Store' in files:
    files.remove('.DS_Store')
  with open(load_dir+'/metadata.json') as f:    
    meta = json.load(f)
    assigned = meta["assigned"]
    unassigned = meta["unassigned"]
    scanned = meta["scanned"]
  files.remove('metadata.json')

  data = {}
  for file in files:
    with open(load_dir+"/"+file) as f:
      data.update(json.load(f))
      print str(len(data)) + " colors loaded..."
  print "Loading complete!"


def multiload(count):
  global data, assigned, unassigned, scanned
  data = []
  assigned = []
  unassigned = []
  scanned = []

  for i in range(count):
    print "Loading data_part"+str(i)+"..."
    load_dir = data_dir+"_part"+str(i)
    files = [f for f in listdir(load_dir) if isfile(join(load_dir, f))]
    if '.DS_Store' in files:
      files.remove('.DS_Store')
    with open(load_dir+'/metadata.json') as f:    
      meta = json.load(f)
      assigned.append(meta["assigned"])
      unassigned.append(meta["unassigned"])
      scanned.append(meta["scanned"])
    files.remove('metadata.json')

    section_data = {}
    for file in files:
      with open(load_dir+"/"+file) as f:
        section_data.update(json.load(f))
        print str(len(section_data)) + " colors loaded..."
    data.append(section_data)
  print "Loading complete!"


def merge():
  global data, assigned, unassigned, scanned
  print "Starting merge..."
  complete = {}
  usedfiles = []

  if len(data) == 0:
    return

  print "Merging section 0"
  complete = data[0]
  complete_assigned = assigned[0]
  complete_unassigned = unassigned[0]

  count = 0
  perc = 0
  for r in complete:
    for g in complete[r]:
      for b in complete[r][g]:
        if complete[r][g][b]:
          file = complete[r][g][b].split('&')[0]
          if file not in usedfiles:
            usedfiles.append(file)
    count += 1
    new_perc = int(round(((count * 1.0) / rng) * 100))
    if new_perc > perc and new_perc%10==0:
      print str(new_perc)+"%"
    perc = new_perc
  print "Section merge complete"
  print "Starting with "+str(len(usedfiles))+" scanned and "+str(round(((complete_assigned * 1.0) / (rng*rng*rng)) * 100, 2))+ "%"

  update = True
  for i in range(1,len(data)):
    count = 0
    perc = 0
    print "Merging section "+str(i)
    section = data[i]
    for r in section:
      for g in section[r]:
        for b in section[r][g]:
            if complete[r][g][b] and section[r][g][b] and update:
              update = False
              color_data = section[r][g][b]
              complete[r][g][b] = color_data
              file = color_data.split('&')[0]
              if file not in usedfiles:
                usedfiles.append(file)
            elif complete[r][g][b] and section[r][g][b]:
              color_data = section[r][g][b]
              file = color_data.split('&')[0]
              if file not in usedfiles:
                complete[r][g][b] = color_data
                usedfiles.append(file)
              else:
                update = True
            elif section[r][g][b]:
              color_data = section[r][g][b]
              complete[r][g][b] = color_data
              file = color_data.split('&')[0]
              if file not in usedfiles:
                usedfiles.append(file)
              complete_assigned += 1
              complete_unassigned -= 1
      count += 1
      new_perc = int(round(((count * 1.0) / rng) * 100))
      if new_perc > perc and new_perc%10==0:
        print str(new_perc)+"%"
      perc = new_perc
  scanned = len(usedfiles)
  assigned = complete_assigned
  unassigned = complete_unassigned
  data = complete
  print "Ending with "+str(scanned)+" scanned and "+str(round(((assigned * 1.0) / (rng*rng*rng)) * 100, 2))+ "%"


def generalize():
  global data, unassigned, assigned
  print "Generalization starting with " + str(assigned) + " assigned values..."
  spread = 3
  perc = round(0.0, 1)
  perc_c = round(0.0, 1)
  for r in range(rng):
    for g in range(rng):
      for b in range(rng):
        if data[str(r)][str(g)][str(b)] and "*" not in data[str(r)][str(g)][str(b)]:
          for r2 in range(r-spread,r+spread+1):
            for g2 in range(g-spread,g+spread+1):
              for b2 in range(b-spread,b+spread+1):
                if r2 >= 0 and r2 < rng and g2 >= 0 and g2 < rng and b2 >= 0 and b2 < rng:
                  if data[str(r2)][str(g2)][str(b2)] is None or (r2 >= r and g2 >= g and b2 >= b and "*" in data[str(r2)][str(g2)][str(b2)]):
                    if data[str(r2)][str(g2)][str(b2)] is None:
                      assigned+=1
                      unassigned-=1
                      new_perc = round(((assigned * 1.0) / (rng*rng*rng)) * 100, 1)
                      if new_perc > perc:
                        print "... " + str(new_perc) + "%"
                      perc = new_perc
                    data[str(r2)][str(g2)][str(b2)] = data[str(r)][str(g)][str(b)]+"&*"
                    new_perc_c = int(((r+1 * 1.0) / rng) * 100)
                    if new_perc_c > perc_c:
                      print "Color Completion: " + str(new_perc_c) + "%"
                    perc_c = new_perc_c
  print "Generalization complete with " + str(assigned) + " total assigned values!"


def init():
  global data, unassigned, assigned
  print "Initializing data..."
  data = [[[None for blue in range(rng)] for green in range(rng)] for red in range(rng)]
  # data = [[['null' for blue in range(rng)] for green in range(rng)] for red in range(rng)]
  # data = [[['img6000.jpg&1000&1000' for blue in range(rng)] for green in range(rng)] for red in range(rng)]
  unassigned = crng * crng * crng
  print str(unassigned) + " unassigned colors and "+ str(assigned) + " assigned colors."


def reset(index = None):
  global data, unassigned, assigned, data_index
  if index:
    data_index = "_part"+index
  data = None;
  unassigned = 0
  assigned = 0
  try:
    open(data_dir+data_index+"/metadata.json", 'w').close()
  except:
    pass
  if exists(data_dir+data_index):
    shutil.rmtree(data_dir+data_index)
  print "Data reset."


def write():
  print "writing: "+data_dir+data_index
  if not exists(data_dir+data_index):
    makedirs(data_dir+data_index)
  if data == None:
    print "Data not initialized yet. Aborting."
    return
  print "Writing data to files..."
  perc = 0
  limitter = 0
  lrng = 52
  filenum = 0
  while limitter<rng:
    limit = limitter + lrng
    if limit > rng:
      limit = rng
    if limitter == limit:
      break;
    with open(data_dir+data_index+"/"+str(filenum)+".json", 'w') as f:
      f.write("{")
      for r in range(limitter, limit):
        f.write("\n  \""+str(r)+"\":{")
        for g in range(rng):
          f.write("\n    \""+str(g)+"\":{")
          for b in range(rng):
            f.write("\n      \""+str(b)+"\":")
            if type(data) is dict and data[str(r)][str(g)][str(b)]:
              line = json.dumps(data[str(r)][str(g)][str(b)], ensure_ascii=False)
              f.write(line)
            elif type(data) is not dict and data[r][g][b]:
              line = json.dumps(data[r][g][b], ensure_ascii=False)
              f.write(line)
            else:
              f.write("null")
            if b < crng:
                f.write(",")
          f.write("\n    }")
          if g < crng:
            f.write(",")
        f.write("\n  }")
        if r < limit-1:
            f.write(",")
        new_perc = int(((r+1 * 1.0) / rng) * 100)
        if new_perc > perc + 4:
          print "... " + str(new_perc) + "%"
          perc = new_perc
      f.write("\n}")
      f.close()
    limitter += lrng
    filenum += 1
    if limitter > crng:
      break

  print "Writing metadata to file..."
  with open(data_dir+data_index+"/metadata.json", 'w') as f:
    line = json.dumps({'scanned':scanned, 'assigned':assigned, 'unassigned':unassigned, 'files':(filenum+1)}, ensure_ascii=False)
    f.write(line)
    f.close()
  print "Writing complete!"


def analyze(index = None):
  global scanned, data, unassigned, assigned, data_index
  if data == None:
    print "Data not initialized yet."
    init()
  images = [f for f in listdir(analyze_path) if isfile(join(analyze_path, f))]
  if '.DS_Store' in images:
    images.remove('.DS_Store')
  if index:
    data_index = "_part"+index
    images = numpy.array_split(images,5)[int(index)].tolist()
  
  print str(len(images)) + " images queued..."
  write_iteration = 5.0
  usedfiles = []
  perc = round(0.0, 2)
  while len(images) > 0 and unassigned > 0:
    perc_start = perc
    file = random.choice(images)
    if debug:
      print file
    image = None
    while not image:
      try:
        image = Image.open(join(analyze_path, file))
      except:
        print "ERROR: File not found: " + str(join(analyze_path, file))
        raw_input("Press enter to continue when reconnected ");
    pixels = image.load()
    size = image.size
    try:
      for x in range(size[0]):
        for y in range(size[1]):
          r = pixels[x,y][0]
          g = pixels[x,y][1]
          b = pixels[x,y][2]
          if not data[r][g][b]:
            data[r][g][b] = file+'&'+str(x)+'&'+str(y)+'&'+str(size[0])+'&'+str(size[1])
            if not file in usedfiles:
              scanned += 1
              usedfiles.append(file)
            unassigned -= 1
            assigned += 1
          new_perc = round(((assigned * 1.0) / (rng*rng*rng)) * 100, 2)
          if new_perc > perc:
            print "... " + str(new_perc) + "%"
            if new_perc%write_iteration==0:
              write_iteration*=2
              write()
          perc = new_perc
          if len(images)>1 and perc-perc_start>0.01:
            raise BreakIt
      images.remove(file)
      print "... " + file + " done, "+str(len(images))+" images left ("+ str(perc)+"%)"
    except BreakIt:
      print "... too many colors in "+file+", moving to next."
      
  print "Analysis complete!"
  print str(unassigned) + " unassigned colors and "+ str(assigned) + " assigned colors."


def test():
  pass


while True:
  print "0: Auto (New Full Analysis)"
  print "1: Analyze images"
  print "2: Init data"
  print "3: Save data"
  print "4: Reset data and file"
  print "5: Load and generalize data"
  print "6: Multiload and generalize data"
  print "7: Exit (without saving)"
  choice = (int)(raw_input("> "))

  if choice == 0:
    print "Are you sure you want to reset data? (y=1/n=0)"
    choice = (int)(raw_input("> "))
    if choice == 1:
      choice = raw_input("Folder section: ")
      reset(choice)
      init()
      analyze(choice)
      write()
    else:
      print "Aborting"
    
  elif choice == 1:
    choice = raw_input("Folder section: ")
    analyze(choice)
  elif choice == 2:
    init()
  elif choice == 3:
    write()
  elif choice == 4:
    print "Are you sure you want to reset data? (y=1/n=0)"
    choice = (int)(raw_input("> "))
    if choice == 1:
      reset()
    else:
      print "Aborting"
  elif choice == 5:
    load()
    generalize()
    write()
  elif choice == 6:
    multiload(5)
    merge()
    generalize()
    write()
  elif choice == 7:
    break
  elif choice == 626:
    test()
  else:
    print ""

  print ""