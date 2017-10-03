# LSMetrics v 1.0.0 Garbage

#-------------------------------------------

def createBinarios_single(ListMapBins, prepareBIODIM):
    """
    This function reclassify an input map into a binary map, according to reclassification rules passed by
    a text file
    """
    readtxt = selectdirectory()
    grass.run_command('g.region', rast=ListMapBins)
    grass.run_command('r.reclass', input=ListMapBins, output=ListMapBins+'_HABMAT', 
                      rules=readtxt, overwrite = True)

    if prepareBIODIM:
        mapsList = grass.list_grouped ('rast', pattern='(*)') ['userbase']
    else:
        mapsList = grass.list_grouped ('rast', pattern='(*)') ['PERMANENT']  
    return readtxt

#-------------------------------------------

def createBinarios(ListMapBins, prepareBIODIM):
    """
    This function reclassify a series of input maps into binary maps, according to reclassification rules passed by
    a text file
    """
    readtxt = selectdirectory()
    for i in ListMapBins:
        grass.run_command('g.region',rast=i)
        grass.run_command('r.reclass',input=i,output=i+'_HABMAT',rules=readtxt, overwrite = True)
        if prepareBIODIM:
            mapsList=grass.list_grouped ('rast', pattern='(*)') ['userbase']
        else:
            mapsList=grass.list_grouped ('rast', pattern='(*)') ['current_mapset']    
        return readtxt

#-------------------------------------------

def create_habmat_single(ListMapBins_in, prefix, dirout, list_habitat_classes, prepareBIODIM, calcStatistics):

    """
  Function for a single map
  This function reclassify an input map into a binary map, according to reclassification rules passed by
  a text file
  """

    ListMapBins = prefix+ListMapBins_in

    # opcao 1: ler um arquivo e fazer reclass
    # TEMOS QUE ORGANIZAR ISSO AINDA!!
    #readtxt=selectdirectory()
    #grass.run_command('g.region',rast=ListMapBins)
    #grass.run_command('r.reclass',input=ListMapBins,output=ListMapBins+'_HABMAT',rules=readtxt, overwrite = True)

    # opcao 2: definir quais classes sao habitat; todas as outras serao matriz
    if(len(list_habitat_classes) > 0):

        conditional = ''
        cc = 0
        for j in list_habitat_classes:
            if cc > 0:
                conditional = conditional+' || '
            conditional = conditional+ListMapBins_in+' == '+j
            cc += 1

        expression = ListMapBins+'_HABMAT = if('+conditional+', 1, 0)'
        grass.run_command('g.region', rast=ListMapBins_in)
        grass.mapcalc(expression, overwrite = True, quiet = True)
        grass.run_command('r.null', map=ListMapBins+'_HABMAT', null='0') # precisa disso??, nao sei .rsrs 
    else:
        print 'You did not type which class is habitat!! Map not generated' # organizar para dar um erro; pode ser com try except 

    if prepareBIODIM:
        create_TXTinputBIODIM([ListMapBins+'_HABMAT'], outputfolder, "simulados_HABMAT")
    else:
        grass.run_command('g.region', rast=ListMapBins+'_HABMAT')
        grass.run_command('r.out.gdal', input=ListMapBins+'_HABMAT', out=ListMapBins+'_HABMAT.tif',overwrite = True)

    if calcStatistics:
        createtxt(ListMapBins+'_HABMAT', dirout, ListMapBins+'_HABMAT')
        
#-------------------------------------------
def exportPNG(mapinp=[]):
    """ 
    This function exports a series of raster maps as png images
    """
    lista_png=[]
    for i in mapinp:
        grass.run_command('r.out.png',input=i,out=i)
        lista_png.append(i+'.png')
    return lista_png        
        
    

#----------------------------------------------------------------------------------
# Metrics for patch size/area/ID (PATCH)

def patchSingle(Listmapspatch_in, prefix,dirout,prepareBIODIM,calcStatistics,removeTrash):
    """
    Function for a single map
    This function calculates area per patch in a map (PATCH), considering structural connectivity 
    (no fragmentation or dilatation):
    - generates and exports maps with Patch ID and Area of each patch
    - generatics statistics - Area per patch (if calcStatistics == True)
    """

    Listmapspatch = prefix+Listmapspatch_in

    grass.run_command('g.region', rast=Listmapspatch_in)
    grass.run_command('r.clump', input=Listmapspatch_in, output=Listmapspatch+"_patch_clump", overwrite = True)
    ########## essa proxima linha muda algo?? clump * mata/nao-mata  
    expression12=Listmapspatch+"_patch_clump_mata = "+Listmapspatch+"_patch_clump*"+Listmapspatch_in
    grass.mapcalc(expression12, overwrite = True, quiet = True)
    expression13=Listmapspatch+"_patch_clump_mata_limpa_pid = if("+Listmapspatch+"_patch_clump_mata > 0, "+Listmapspatch+"_patch_clump_mata, null())"
    grass.mapcalc(expression13, overwrite = True, quiet = True)

    nametxtreclass=rulesreclass(Listmapspatch+"_patch_clump_mata_limpa_pid", dirout)
    grass.run_command('r.reclass', input=Listmapspatch+"_patch_clump_mata_limpa_pid", output=Listmapspatch+"_patch_clump_mata_limpa_AreaHA", rules=nametxtreclass, overwrite = True)
    os.remove(nametxtreclass)

    if prepareBIODIM:
        #grass.run_command('r.out.gdal',input=Listmapspatch+"_patch_clump_mata_limpa",out=Listmapspatch+"_patch_PID.tif")
        create_TXTinputBIODIM([Listmapspatch+"_patch_clump_mata_limpa_pid"], "simulados_HABMAT_grassclump_PID", dirout)
        create_TXTinputBIODIM([Listmapspatch+"_patch_clump_mata_limpa_AreaHA"], "simulados_HABMAT_grassclump_AREApix", dirout)    
    else:
        grass.run_command('g.region', rast=Listmapspatch+"_patch_clump_mata_limpa_AreaHA")
        grass.run_command('r.out.gdal', input=Listmapspatch+"_patch_clump_mata_limpa_AreaHA", out=Listmapspatch+"_patch_AreaHA.tif",overwrite = True)

    if calcStatistics:
        createtxt(Listmapspatch+"_patch_clump_mata_limpa_pid", dirout, Listmapspatch+"_patch_AreaHA")

    if removeTrash:
        if prepareBIODIM:
            txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata"]
        else:
            txts = [Listmapspatch+"_patch_clump", Listmapspatch+"_patch_clump_mata"] #, Listmapspatch+"_patch_clump_mata_limpa_pid"]
        for txt in txts:
            grass.run_command('g.remove', type="raster", name=txt, flags='f')
            
            
#-------------------------------------------

def areaFragSingle(map_HABITAT_Single, prefix, dirout, list_esc_areaFrag, 
                   prepareBIODIM, calcStatistics, removeTrash):
    """
    Function for a single map
    This function fragments patches (FRAG), excluding corridors and edges given input scales (distances), and:
    - generates and exports maps with Patch ID and Area of each "fragmented" patch
    - generatics statistics - Area per patch (if calcStatistics == True)
    """

    ListmapsFrag = prefix+map_HABITAT_Single

    grass.run_command('g.region', rast=map_HABITAT_Single)
    Lista_escalafragM, listmeters = escala_frag(map_HABITAT_Single,list_esc_areaFrag)

    x=0
    for a in Lista_escalafragM:

        meters=int(listmeters[x])  
        #print escalafragM
        grass.run_command('r.neighbors', input=map_HABITAT_Single, output=ListmapsFrag+"_ero_"+`meters`+'m', method='minimum', size=a, overwrite = True)
        grass.run_command('r.neighbors', input=ListmapsFrag+"_ero_"+`meters`+'m', output=ListmapsFrag+"_dila_"+`meters`+'m', method='maximum', size=a, overwrite = True)
        expression1=ListmapsFrag+"_FRAG"+`meters`+"m_mata = if("+ListmapsFrag+"_dila_"+`meters`+'m'+" > 0, "+ListmapsFrag+"_dila_"+`meters`+'m'+", null())"
        grass.mapcalc(expression1, overwrite = True, quiet = True)
        expression2=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo = if("+map_HABITAT_Single+" >= 0, "+ListmapsFrag+"_FRAG"+`meters`+"m_mata, null())"
        grass.mapcalc(expression2, overwrite = True, quiet = True)
        grass.run_command('r.clump', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo", output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", overwrite = True)

        grass.run_command('g.region', rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid")
        nametxtreclass=rulesreclass(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", dirout)
        grass.run_command('r.reclass', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", output=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA", rules=nametxtreclass, overwrite = True)   
        os.remove(nametxtreclass)

        # identificando branch tampulins e corredores


        expression3='temp_BSSC=if(isnull('+ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA"+'),'+map_HABITAT_Single+')'
        grass.mapcalc(expression3, overwrite = True, quiet = True)    

        expression1="MapaBinario=temp_BSSC"
        grass.mapcalc(expression1, overwrite = True, quiet = True)    
        grass.run_command('g.region',rast="MapaBinario")
        expression2="A=MapaBinario"
        grass.mapcalc(expression2, overwrite = True, quiet = True)
        grass.run_command('g.region',rast="MapaBinario")
        expression3="MapaBinario_A=if(A[0,0]==0 && A[0,-1]==1 && A[1,-1]==0 && A[1,0]==1,1,A)"
        grass.mapcalc(expression3, overwrite = True, quiet = True)
        expression4="A=MapaBinario_A"
        grass.mapcalc(expression4, overwrite = True, quiet = True)
        expression5="MapaBinario_AB=if(A[0,0]==0 && A[-1,0]==1 && A[-1,1]==0 && A[0,1]==1,1,A)"
        grass.mapcalc(expression5, overwrite = True, quiet = True) 
        expression6="A=MapaBinario_AB"
        grass.mapcalc(expression6, overwrite = True, quiet = True)
        expression7="MapaBinario_ABC=if(A[0,0]==0 && A[0,1]==1 && A[1,1]==0 && A[1,0]==1,1,A)"
        grass.mapcalc(expression7, overwrite = True, quiet = True)
        expression8="A=MapaBinario_ABC"
        grass.mapcalc(expression8, overwrite = True, quiet = True)
        expression9="MapaBinario_ABCD=if(A[0,0]==0 && A[1,0]==1 && A[1,1]==0 && A[0,1]==1,1,A)"
        grass.mapcalc(expression9, overwrite = True, quiet = True)

        expression4='MapaBinario_ABCD1=if(MapaBinario_ABCD==0,null(),1)'
        grass.mapcalc(expression4, overwrite = True, quiet = True)    
        grass.run_command('r.clump', input='MapaBinario_ABCD1', output="MapaBinario_ABCD1_pid", overwrite = True)

        grass.run_command('r.neighbors', input='MapaBinario_ABCD1_pid', output='MapaBinario_ABCD1_pid_mode', method='mode', size=3, overwrite = True)
        grass.run_command('r.cross', input=ListmapsFrag+"_FRAG"+`meters`+'m_mata_clump_pid,MapaBinario_ABCD1_pid_mode',out=ListmapsFrag+"_FRAG"+`meters`+'m_mata_clump_pid_cross_corredor',overwrite = True)
        cross_TB = grass.read_command('r.stats', input=ListmapsFrag+"_FRAG"+`meters`+'m_mata_clump_pid_cross_corredor', flags='l')  # pegando a resolucao
        print cross_TB 
        txt=open("table_cross.txt",'w')
        txt.write(cross_TB)
        txt.close()

        reclass_frag_cor('MapaBinario_ABCD1_pid', dirout)

        expression10='MapaBinario_ABCD1_pid_reclass_sttepings=if(isnull(MapaBinario_ABCD1_pid_reclass)&&temp_BSSC==1,3,MapaBinario_ABCD1_pid_reclass)'
        grass.mapcalc(expression10, overwrite = True, quiet = True)    
        expression11='MapaBinario_ABCD1_pid_reclass_sttepings2=if(temp_BSSC==1,MapaBinario_ABCD1_pid_reclass_sttepings,null())'
        grass.mapcalc(expression11, overwrite = True, quiet = True)     




        if prepareBIODIM:
            #grass.run_command('r.out.gdal',input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid",out=ListmapsFrag+"_FRAG"+`meters`+"m_PID.tif")
            create_TXTinputBIODIM([ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid"], "simulados_HABMAT_FRAC_"+`meters`+"m_PID", dirout)
            create_TXTinputBIODIM([ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA"], "simulados_HABMAT_FRAC_"+`meters`+"m_AREApix", dirout)
        else:
            grass.run_command('g.region', rast=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA")
            grass.run_command('r.out.gdal', input=ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_AreaHA", out=ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA.tif",overwrite = True)      

        if calcStatistics:
            createtxt(ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid", dirout, ListmapsFrag+"_FRAG"+`meters`+"m_AreaHA")        

        if removeTrash:
            if prepareBIODIM:
                txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo"]
            else:
                txts = [ListmapsFrag+"_ero_"+`meters`+'m', ListmapsFrag+"_dila_"+`meters`+'m', ListmapsFrag+"_FRAG"+`meters`+"m_mata", ListmapsFrag+"_FRAG"+`meters`+"m_mata_lpo"] #, ListmapsFrag+"_FRAG"+`meters`+"m_mata_clump_pid"]
            for txt in txts:
                grass.run_command('g.remove', type="raster", name=txt, flags='f')
        x=x+1     




#-------------------------------------------

def areaconSingle(mapHABITAT_Single, prefix, dirout, escala_frag_con,
                  prepareBIODIM, calcStatistics, removeTrash):

    os.chdir(dirout)
    """
  Function for a single map
  This function calculates functional patch area in a map (CON), considering functional connectivity 
  (dilatation of edges given input scales/distances), and:
  - generates and exports maps with Patch ID and Area of each patch
  - generatics statistics - Area per patch (if calcStatistics == True)
  """

    Listmapspatch = prefix+mapHABITAT_Single

    grass.run_command('g.region', rast=mapHABITAT_Single)
    listescalafconM, listmeters = escala_con(mapHABITAT_Single, escala_frag_con)

    x=0
    for a in listescalafconM:
        meters = int(listmeters[x])
        grass.run_command('r.neighbors', input=mapHABITAT_Single, output=Listmapspatch+"_dila_"+`meters`+'m_orig', method='maximum', size=a, overwrite = True)
        expression=Listmapspatch+"_dila_"+`meters`+'m_orig_temp = if('+Listmapspatch+"_dila_"+`meters`+'m_orig == 0, null(), '+Listmapspatch+"_dila_"+`meters`+'m_orig)'
        grass.mapcalc(expression, overwrite = True, quiet = True)
        grass.run_command('r.clump', input=Listmapspatch+"_dila_"+`meters`+'m_orig_temp', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', overwrite = True)
        espressao1=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata = '+mapHABITAT_Single+'*'+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid'
        grass.mapcalc(espressao1, overwrite = True, quiet = True)
        espressao2=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid = if('+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata > 0, '+Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata, null())'
        grass.mapcalc(espressao2, overwrite = True, quiet = True)

        nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', dirout)
        grass.run_command('r.reclass', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', rules=nametxtreclass, overwrite = True)
        os.remove(nametxtreclass)

        if prepareBIODIM:
            #grass.run_command('r.out.gdal',input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid',out=Listmapspatch+"_dila_"+`meters`+'m_clean_PID.tif')
            create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid'], dirout, "simulados_HABMAT_grassclump_dila_"+`meters`+"m_clean_PID")
            create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA'], dirout, "simulados_HABMAT_grassclump_dila_"+`meters`+"m_clean_AREApix")

            ########### calculando o area complete, exportanto ele e tb PID complete - precisa tambem gerar um area complete mesmo?
            nametxtreclass=rulesreclass(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid',dirout)
            grass.run_command('r.reclass', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', output=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', rules=nametxtreclass, overwrite = True)
            os.remove(nametxtreclass)
            #grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA', out=Listmapspatch+"_dila_"+`meters`+'m_complete_AreaHA.tif')  
            #grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', out=Listmapspatch+"_dila_"+`meters`+'m_complete_PID.tif')
            create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid'], dirout, "simulados_HABMAT_grassclump_dila_"+`meters`+"m_complete_PID")
            create_TXTinputBIODIM([Listmapspatch+"_dila_"+`meters`+'m_orig_clump_complete_AreaHA'], dirout, "simulados_HABMAT_grassclump_dila_"+`meters`+"m_complete_AREApix")
        else:
            grass.run_command('g.region', rast=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA')
            grass.run_command('r.out.gdal', input=Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_AreaHA', out=Listmapspatch+"_dila_"+`meters`+'m_clean_AreaHA.tif',overwrite = True)     

        if calcStatistics:
            createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata_limpa_pid', dirout, Listmapspatch+"_dila_"+`meters`+"m_clean_AreaHA") # clean
            createtxt(Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', dirout, Listmapspatch+"_dila_"+`meters`+"m_complete_AreaHA") # complete

        if removeTrash:
            if prepareBIODIM:
                txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_temp', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata']
            else:
                txts = [Listmapspatch+"_dila_"+`meters`+'m_orig', Listmapspatch+"_dila_"+`meters`+'m_orig_temp', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_pid', Listmapspatch+"_dila_"+`meters`+'m_orig_clump_mata']
            for txt in txts:
                grass.run_command('g.remove', type="raster", name=txt, flags='f')

        x=x+1


#-------------------------------------------

# funcao de pcts
def PCTs_single(mapbin_HABITAT,escales):
    for i in escales:
        esc=int(i)
        outputname=mapbin_HABITAT+"_PCT_esc_"+`esc`
        windowsize=getsizepx(mapbin_HABITAT, esc)
        grass.run_command('g.region', rast=mapbin_HABITAT)
        grass.run_command('r.neighbors',input=mapbin_HABITAT,out="temp_PCT",method='average',size=windowsize,overwrite = True )
        expression1=outputname+'=temp_PCT*100'
        grass.mapcalc(expression1, overwrite = True, quiet = True)    
        grass.run_command('r.out.gdal', input=outputname, out=outputname+'.tif', overwrite = True)
        grass.run_command('g.remove', type="raster", name='temp_PCT', flags='f')


#-------------------------------------------

def PCTs(Listmap_HABITAT,escales):
    for i in escales:
        esc=int(i)
        for mapHABT in Listmap_HABITAT:
            outputname=mapHABT+"_PCT_esc_"+`esc`
            windowsize=getsizepx(mapHABT, esc)
            grass.run_command('g.region', rast=mapHABT)
            grass.run_command('r.neighbors',input=mapHABT,out="temp_PCT",method='average',size=windowsize,overwrite = True )
            expression1=outputname+'=temp_PCT*100'
            grass.mapcalc(expression1, overwrite = True, quiet = True)    
            grass.run_command('r.out.gdal', input=outputname, out=outputname+'.tif', overwrite = True)
            grass.run_command('g.remove', type="raster", name='temp_PCT', flags='f')

#-------------------------------------------

def dist_edge_Single(Listmapsdist_in, prefix,prepareBIODIM, dirout,removeTrash):
    """
    Function for a single map
    This function calculates the distance of each pixel to habitat edges, considering
    negative values (inside patches) and positive values (into the matrix). Also:
    - generates and exports maps of distance to edge (DIST)
    """

    Listmapsdist = prefix+Listmapsdist_in

    grass.run_command('g.region', rast=Listmapsdist_in)
    expression1=Listmapsdist+'_invert = if('+Listmapsdist_in+' == 0, 1, null())'
    grass.mapcalc(expression1, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=Listmapsdist+'_invert', distance=Listmapsdist+'_invert_forest_neg_eucldist',overwrite = True)
    expression2=Listmapsdist+'_invert_matrix = if('+Listmapsdist_in+' == 0, null(), 1)'
    grass.mapcalc(expression2, overwrite = True, quiet = True)
    grass.run_command('r.grow.distance', input=Listmapsdist+'_invert_matrix', distance=Listmapsdist+'_invert_matrix_pos_eucldist',overwrite = True)
    expression3=Listmapsdist+'_dist = '+Listmapsdist+'_invert_matrix_pos_eucldist-'+Listmapsdist+'_invert_forest_neg_eucldist'
    grass.mapcalc(expression3, overwrite = True, quiet = True)

    if prepareBIODIM:
        create_TXTinputBIODIM([Listmapsdist+'_dist'], dirout, "simulados_HABMAT_DIST")
    else:
        grass.run_command('r.out.gdal', input=Listmapsdist+'_dist', out=Listmapsdist+'_DIST.tif', overwrite = True)

    if removeTrash:
        txts = [Listmapsdist+'_invert', Listmapsdist+'_invert_forest_neg_eucldist', Listmapsdist+'_invert_matrix', Listmapsdist+'_invert_matrix_pos_eucldist']
        for txt in txts:
            grass.run_command('g.remove', type="raster", name=txt, flags='f')

#-------------------------------------------

def create_EDGE_single(ListmapsED_in, escale_ed, dirs, prefix,calcStatistics,removeTrash,escale_pct):
    """
    Function for a single map
    This function separates habitat area into edge and interior/core regions, given a scale/distance defined as edge, and:
    - generates and exports maps with each region
    - generatics statistics - Area per region (matrix/edge/core) (if calcStatistics == True)
    """  
    os.chdir(dirs)
    ListmapsED = prefix+ListmapsED_in

    grass.run_command('g.region', rast=ListmapsED_in)
    listsize, listmeters = escala_frag(ListmapsED_in, escale_ed)

    cont_escale=0
    for i in listsize:
        apoioname = int(listmeters[cont_escale])  
        formatnumber='0000'+`apoioname`
        formatnumber=formatnumber[-4:]
        outputname_meco=ListmapsED+'_MECO_'+formatnumber+'m' # nome de saida do mapa edge-core-matriz
        outputname_core=ListmapsED+'_CORE_'+formatnumber+'m' # nome de saida do mapa Core
        outputname_edge=ListmapsED+'_EDGE_'+formatnumber+'m' # nome de saida do mapa edge


        grass.run_command('r.neighbors', input=ListmapsED_in, output=ListmapsED+"_eroED_"+`apoioname`+'m', method='minimum', size=i, overwrite = True)
        inputs=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED_in
        out=ListmapsED+'_EDGE'+`apoioname`+'m_temp1'
        grass.run_command('r.series', input=inputs, out=out, method='sum', overwrite = True)
        espressaoEd=ListmapsED+'_EDGE'+`apoioname`+'m_temp2 = int('+ListmapsED+'_EDGE'+`apoioname`+'m_temp1)' # criando uma mapa inteiro
        mapcalcED(espressaoEd)

        espressaoclip=outputname_meco+'= if('+ListmapsED_in+' >= 0, '+ListmapsED+'_EDGE'+`apoioname`+'m_temp2, null())'
        mapcalcED(espressaoclip)  

        espressaocore=outputname_core+'= if('+outputname_meco+'==2,1,0)'
        grass.mapcalc(espressaocore, overwrite = True, quiet = True)     

        espressaoedge=outputname_edge+'= if('+outputname_meco+'==1,1,0)'
        grass.mapcalc(espressaoedge, overwrite = True, quiet = True)  



        grass.run_command('r.out.gdal', input=outputname_meco, out=outputname_meco+'.tif', overwrite = True) 
        grass.run_command('r.out.gdal', input=outputname_edge, out=outputname_edge+'.tif', overwrite = True)
        grass.run_command('r.out.gdal', input=outputname_core, out=outputname_core+'.tif', overwrite = True)
        print '>>>>>>>>>>>>>>>>>>>>',escale_pct
        if len(escale_pct)>0:
            for pct in escale_pct:
                pctint=int(pct)

                formatnumber='0000'+`pctint`
                formatnumber=formatnumber[-4:]        
                outputname_edge_pct=outputname_edge+'_PCT_esc_'+formatnumber

                size=getsizepx(outputname_edge, pctint)
                grass.run_command('r.neighbors', input=outputname_edge, output="temp_pct", method='average', size=size, overwrite = True)
                espressaoedge=outputname_edge_pct+'=temp_pct*100'
                grass.mapcalc(espressaoedge, overwrite = True, quiet = True)    
                grass.run_command('r.out.gdal', input=outputname_edge_pct, out=outputname_edge_pct+'.tif', overwrite = True)
                grass.run_command('g.remove', type="raster", name='temp_pct', flags='f')





        if calcStatistics:
            createtxt(ListmapsED+'_EDGE'+`apoioname`+'m', dirs, out)


        if removeTrash:
            grass.run_command('g.remove', type="raster", name=ListmapsED+"_eroED_"+`apoioname`+'m,'+ListmapsED+'_EDGE'+`apoioname`+'m_temp1,'+ListmapsED+'_EDGE'+`apoioname`+'m_temp2', flags='f')

        cont_escale=cont_escale+1


#-------------------------------------------


#-------------------------------------------


#-------------------------------------------


#-------------------------------------------


#-------------------------------------------