from samples.models import Library, Libraryfile
from django.core.files import File

file = open("/Users/gramasamy/Downloads/QCfigures/qcinfo_toupload.set1", "r")
for line in file:
	[libcode, subcategory, path] = line.split()
	filename = os.path.basename(path)
	print libcode, subcategory, path, filename
	if Library.objects.filter(library_code=libcode).exists():
		libobj = Library.objects.get(library_code=libcode)
		newlibfileobj = Libraryfile(category="fastqqc", subcategory=subcategory)
		newlibfileobj.library = libobj
		newlibfileobj.file.save(filename, File(open(path)))