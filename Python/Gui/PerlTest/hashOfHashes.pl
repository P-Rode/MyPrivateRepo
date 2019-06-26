

<<<<<<< HEAD
$dirname = "/root/uabrode";
=======
$dirname = "/root/P-Rode";
>>>>>>> branch 'master' of https://github.com/uabrode/MyPrivateRepo.git


sub revFind {
# Gör en metod som har en två input. Directory och CXC:nr
# Den ska returera en possition i arrayen så att man hittar rätt revläge

}

opendir ( DIR, $dirname ) || die "Error in opening dir $dirname\n";

# Store file with name "CXC"
while(($filename = readdir(DIR))){
#( (while$filename = grep{ (CXC.*)(_)(.*) }(DIR))){
	# Gör en regexp av läsningen med två grupper. En 
	# En med filnamn och en med Revläge
	# Spara resultatet i en array av arrayer 
	next if ($filename =~ m/(CXC.*)(_)(.*)/);
	
		print("$filename\n");

}
closedir(DIR);

