

<<<<<<< HEAD
$dirname = "/root/uabrode";
=======
$dirname = "/root/P-Rode";
>>>>>>> branch 'master' of https://github.com/uabrode/MyPrivateRepo.git


sub revFind {
# G�r en metod som har en tv� input. Directory och CXC:nr
# Den ska returera en possition i arrayen s� att man hittar r�tt revl�ge

}

opendir ( DIR, $dirname ) || die "Error in opening dir $dirname\n";

# Store file with name "CXC"
while(($filename = readdir(DIR))){
#( (while$filename = grep{ (CXC.*)(_)(.*) }(DIR))){
	# G�r en regexp av l�sningen med tv� grupper. En 
	# En med filnamn och en med Revl�ge
	# Spara resultatet i en array av arrayer 
	next if ($filename =~ m/(CXC.*)(_)(.*)/);
	
		print("$filename\n");

}
closedir(DIR);

