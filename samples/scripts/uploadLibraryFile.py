newlibraryfileobj = Libraryfile()
newlibraryfileobj.library=Library.objects.get(library_code="PA002")
newlibraryfileobj.category="fastqqc"
newlibraryfileobj.subcategory="test"
newlibraryfileobj.file.save("PA002_Lane1_fastqStats.png", File(open('/Users/gramasamy/Downloads/PA001_Lane1_tileAverage.png')))