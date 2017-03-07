import sys
import string
import math
import os
from os.path import isfile, join

def main():

    if len( sys.argv ) == 1:
        print ( "usage: " + sys.argv[0] + " <list of files>" )
        print ( "       " + sys.argv[0] + " -d <directory with files>" )
        return

    files = {}  # a dictionary which uses diffraction sphere designations as keys
                # value is currently an array of two arrays which contain
                # data imported from the files

                # format of data: intensity, x, y, z
    if len( sys.argv ) == 3 and sys.argv[1] == '-d':
        mypath = sys.argv[2]
        filelist = [f for f in os.listdir( mypath ) if isfile( join( mypath, f ) )]
    else:
        filelist = sys.argv[1:]
    for i in range( 0, len( filelist ) ):
        temp = str.split( filelist[i], '/' )
        temp = temp[len( temp ) - 1]
        temp = str.split( temp, '_' )

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

        for j in range( 0, 2 ):
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

    # print( files )

    for filekey in files.keys():
        center_intensity_index = 0 # storing the index so we can get the x, y, and z values
                                   # this will be some entry in the "perfect" data
        center_intensity = center_x = center_y = center_z = 0
        for j in range( 0, 2 ):
            # print( filekey + ' (' + files[filekey][j][1] + ')' )
            intensity_column = files[filekey][j][2]
            x_column = files[filekey][j][3]
            y_column = files[filekey][j][4]
            z_column = files[filekey][j][5]
            extras = files[filekey][j][6]
            # check intensities to prove differences
            intensity_sum = 0.0
            for k in range( 0, len( intensity_column ) ):
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
        for j in range( 0, 2 ):
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
            for k in range( 0, len( intensity_column ) ):
                if intensity_column[k] < 60000:
                    continue
                distance = math.sqrt( math.pow( center_x - x_column[k], 2 ) + 
                                      math.pow( center_y - y_column[k], 2 ) +
                                      math.pow( center_z - z_column[k], 2 ) )
                # print distance
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
    print('Analysed ' + str( len( filelist ) ) + ' files.')
    print('Results saved to pba-output.csv.')

if __name__== '__main__':
    main()
