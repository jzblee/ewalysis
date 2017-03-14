import sys
import string
import math
import os
from os.path import isfile, join

files = {}  # a dictionary which uses diffraction sphere designations as keys
                # value is currently an array of two arrays which contain
                # data imported from the files

                # format of data: intensity, x, y, z
filelist = []

def read():
    global files
    global filelist
    if len( sys.argv ) == 1:
        print ( 'usage: ' + sys.argv[0] + ' <list of files>' )
        print ( '       ' + sys.argv[0] + ' -d <directory with files>' )
        sys.exit(0)

    if len( sys.argv ) == 3 and sys.argv[1] == '-d':
        mypath = sys.argv[2]
        filelist = [f for f in os.listdir( mypath ) if isfile( join( mypath, f ) )]
    else:
        mypath = ''
        filelist = sys.argv[1:]
    for i in range( len( filelist ) ):
        temp = str.split( filelist[i], '/' )
        temp = temp[len( temp ) - 1]
        temp = str.split( temp, '_' )
        if len( temp ) < 3:
            print ( 'error: invalid file name \'' + filelist[i] + '\'' )
            sys.exit(0)

        # format of temp:
        #   temp[0] - test descriptor
        #   temp[1] - diffraction sphere designation
        #   temp[2] - data classification

        if files.get( temp[1] ) is None:
            files[temp[1]] = []
        files[temp[1]].append( [i, temp[0]] )
    # print (files)

    for filekey in files.keys():

        # print ( '>>> IMPORTING ' + filekey )

        for j in range( 2 ):
            filename = filelist[files[filekey][j][0]]
            # print( filename )
            file = open( join( mypath, filename ), mode='r')
            line = str( file.readline() ).strip( '\n' )
            intensity_column = []
            x_column = []
            y_column = []
            z_column = []
            extras = []
            center = []
            files[filekey][j].append( intensity_column )
            files[filekey][j].append( x_column )
            files[filekey][j].append( y_column )
            files[filekey][j].append( z_column )
            files[filekey][j].append( extras )
            files[filekey][j].append( center )

            while line != '':
                line = str( line ).strip( '\n' )
                new_row = str.split( line, ',' )
                assert ( len( new_row ) == 4 ), 'Incorrect column counts!'
                intensity_column.append( float( new_row[0] ) )
                x_column.append( float( new_row[1] ) )
                y_column.append( float( new_row[2] ) )
                z_column.append( float( new_row[3] ) )
                line = file.readline()
            file.close()


            equal_column_length = ( len( intensity_column ) == len( x_column ) and
                                    len( intensity_column ) == len( y_column ) and
                                    len( intensity_column ) == len( z_column ) )
            assert equal_column_length , 'Inconsistent column lengths!'
    print('Detected ' + str( len( filelist ) ) + ' files.')

def pba():
    global files
    global filelist
    for filekey in files.keys():
        center_intensity_index = 0 # storing the index so we can get the x, y, and z values
                                   # this will be some entry in the 'perfect' data
        center_intensity = center_x = center_y = center_z = 0
        for j in range( 2 ):
            # print( filekey + ' (' + files[filekey][j][1] + ')' )
            intensity_column = files[filekey][j][2]
            x_column = files[filekey][j][3]
            y_column = files[filekey][j][4]
            z_column = files[filekey][j][5]
            extras = files[filekey][j][6]
            # check intensities to prove differences
            intensity_sum = 0.0
            for k in range( len( intensity_column ) ):
                intensity_sum += intensity_column[k]
                if j == 1 and intensity_column[center_intensity_index] < intensity_column[k]:
                    center_intensity_index = k

            if j == 1:
                center_intensity = intensity_column[center_intensity_index]
                center_x = x_column[center_intensity_index]
                center_y = y_column[center_intensity_index]
                center_z = z_column[center_intensity_index]
            extras.append( 0 )
            extras.append( 0 )
            extras.append( intensity_sum )
            # print( str( center_intensity ) + ', ' + str( center_x ) + ', ' + str( center_y ) + ', ' + str( center_z ) )
        for j in range( 2 ):
            intensity_column = files[filekey][j][2]
            x_column = files[filekey][j][3]
            y_column = files[filekey][j][4]
            z_column = files[filekey][j][5]
            extras = files[filekey][j][6]
            center = files[filekey][j][7]
            center.append( center_x )
            center.append( center_y )
            center.append( center_z )
            max_distance = 0.0;
            for k in range( len( intensity_column ) ):
                if intensity_column[k] < 60000:
                    continue
                distance = math.sqrt( math.pow( center_x - x_column[k], 2 ) + 
                                      math.pow( center_y - y_column[k], 2 ) +
                                      math.pow( center_z - z_column[k], 2 ) )
                if max_distance < distance:
                    max_distance = distance
            extras[0] = max_distance
            extras[1] = 4 * math.pi / 3 * math.pow(max_distance, 3)

    output = open('pba-output.csv', mode='w')
    output_row  = 'filekey'
    output_row += ',damaged radius,damaged volume,damaged intensity sum'
    output_row += ',undamaged radius,undamaged volume,undamaged intensity sum'
    output_row += ',delta radius,center x,center y,center z\n'
    output.write(output_row)
    for filekey in files.keys():
        output_row  = filekey
        extras = files[filekey][0][6]
        output_row += ',' + str( extras[0] ) + ',' + str( extras[1] ) + ',' + str( extras[2] )
        extras = files[filekey][1][6]
        output_row += ',' + str( extras[0] ) + ',' + str( extras[1] ) + ',' + str( extras[2] )
        delta = files[filekey][0][6][0] - files[filekey][1][6][0]
        output_row += ',' + str( delta )
        center = files[filekey][0][7]
        output_row += ',' + str( center[0] ) + ',' + str( center[1] ) + ',' + str( center[2] ) + '\n'
        output.write( output_row )
    output.close()
    print('Broadening analysis results saved to pba-output.csv.')

def get_distance(dist_obj):
    return dist_obj[0]

def psa():
    global files
    global filelist

    output = open('psa-output.csv', mode='w')
    output_row  = 'filekey,damaged_int - undamaged_int,distance,damaged_x,damaged_y,damaged_z,undamaged_x,undamaged_y,undamaged_z\n'
    output.write(output_row)

    for filekey in files.keys():
        # print( filekey )
        file0 = files[filekey][0] # usually the 'damaged' test
        file1 = files[filekey][1] # usually the 'perfect' test

        f0_ic = file0[2]
        f1_ic = file1[2]

        f0_xc = file0[3]
        f1_xc = file1[3]

        f0_yc = file0[4]
        f1_yc = file1[4]

        f0_zc = file0[5]
        f1_zc = file1[5]

        f0_points = []
        f1_points = []

        for i in range( len( f0_ic ) ):
            f0_points.append( False )
        for i in range( len( f1_ic ) ):
            f1_points.append( False )
        
        distances = []

        for i in range( len( f0_ic ) ):
            for j in range( len( f1_ic ) ):
                distance = math.sqrt( math.pow( f1_xc[j] - f0_xc[i], 2 ) +
                                      math.pow( f1_yc[j] - f0_yc[i], 2 ) +
                                      math.pow( f1_zc[j] - f0_zc[i], 2 ) )
                new_distance = [distance, i, j]
                distances.append( new_distance )

        possible_pairs = sorted( distances, key=get_distance )

        # print( possible_pairs )

        point_pairs = []

        while possible_pairs: # while list of possible pairs is not empty
            point_pairs.append( possible_pairs[0] )
            f0_ind = possible_pairs[0][1]
            f1_ind = possible_pairs[0][2]
            f0_points[f0_ind] = True
            f1_points[f1_ind] = True
            del possible_pairs[0]
            ppair_ind = 0
            while ppair_ind < len( possible_pairs ):
                if possible_pairs[ppair_ind][1] == f0_ind or possible_pairs[ppair_ind][1] == f1_ind:
                    del possible_pairs[ppair_ind]
                else:
                    ppair_ind = ppair_ind + 1

        for i in range( max( len( f0_ic ), len( f1_ic ) ) ):
            if i < len( f0_ic ):
                if f0_points[i]: # print point in f0 and match in f1
                    for j in range( len( point_pairs ) ):
                        if point_pairs[j][1] == i:
                            break
                    output_row  = filekey
                    output_row += ',' + str( f0_ic[point_pairs[j][1]] - f1_ic[point_pairs[j][2]] )
                    output_row += ',' + str( point_pairs[j][0] )
                    output_row += ',' + str( f0_xc[i] ) + ',' + str( f0_yc[i] ) + ',' + str( f0_zc[i] )
                    output_row += ',' + str( f1_xc[i] ) + ',' + str( f1_yc[i] ) + ',' + str( f1_zc[i] ) + '\n'
                    output.write( output_row )
                else: # print orphan point in f0
                    output_row  = filekey
                    output_row += ',no match found'
                    output_row += ',,' + str( f0_xc[i] ) + ',' + str( f0_yc[i] ) + ',' + str( f0_zc[i] )
                    output_row += ',,,\n'
                    output.write( output_row )
            if i < len( f1_ic ) and not f1_points[i]: # print orphan point in f1
                output_row  = filekey
                output_row += ',no match found'
                output_row += ',,,,'
                output_row += ',' + str( f1_xc[i] ) + ',' + str( f1_yc[i] ) + ',' + str( f1_zc[i] ) + '\n'
                output.write( output_row )

    output.close()
    print('Shifting analysis results saved to psa-output.csv.')

def main():

    read()
    pba()
    psa()

    # print( files )

if __name__== '__main__':
    main()
