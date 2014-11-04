#!/usr/bin/perl -w

# written by dhse979@cse.unsw.edu.au Oct 2014 
# FOR COMP2041 ASSIGNMENT

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
#use CGI::Cookie;
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
# some globals used through the script
$debug = 0;
$students_dir = "./students";

#This is where all the magic happens ===========================================================================

if (defined param('logout_button')) {
	# when logged out we generate the log in screen and all params are forgotten.
	# this is done by not printing any params on the login HTML.
	print login_screen_html("");
	
} elsif (defined param('search_button')) {
	#if search_button was pressed, we pushing the 
	# action_search which has its value as the user input.
	index_screen('action_search');

} elsif (defined param('view_profile_button')) {
	# if view profile button was pressed this will generate their profile page.
	# data is pasted through param.
	# when button is pressed it will pass through the username of the person
	# though the button value.
	$profile_selected = param('view_profile_button');
	browse_screen($profile_selected);

} elsif (defined param('back_button')) {
	#if back_button was pressed on the profile page
	index_screen('action_back');

} elsif (defined param('prev_button')) {
	#if previous button was pressed on the index_page
	index_screen('action_previous'); 

} elsif (defined param('next_button')) {	
	#if next button was pressed on the index_page
	index_screen('action_next');

} elsif (defined param('login_button')) {

	if(check_login(param('username'))) {
		#if log in was pressed and successfully log in
		index_screen('action_logged_in');

	} else {
		#if log in was pressed but failed to log in
		incorrect_login_screen();

	}

} elsif (!defined param('login_button')) {
	#logs in ""<- input to tell the HTML screen to not generate a login fail message.
	login_screen_html("");

} else {
	#This if statement should never popup only used during the early stages of development.
	print center(h2("ops error occurred"));

}

#ignore only for debugging
if($debug) {

	print header;
	foreach $profile (@display_profiles) {
		print "MAIN: $profile ;";
	}
	print br();
	@names = param;
	foreach $name (@names) {
		print "$name = ";
		print param($name);
		print br();
	}
	print page_trailer();
}


#==========================================================================================================================
#THESE SUBROUTINES PASS DATA WITH FORMATTING TO THE HTML

#generates incorrect_login_screen page with a message.
sub incorrect_login_screen {
	$fail_login_message = "Incorrect username or password";
	login_screen_html($fail_login_message);
}

# searches the student's profile from user input and outputs either
# empty when no user input is detected
# not_found when user input of a profile is not found in the database
# passes the student if user input found a profile
sub search_profile_function {
	my ($profile_name) = @_;
	
	if ($profile_name eq "") {
		$return_path = "empty";
	} elsif (-d "./students/$profile_name") {
		$return_path = "./students/$profile_name";
	} else {
		$return_path = "not_found";	
	}

	return $return_path;

}

# generates the set of students to be displayed and returns it into a list.

sub display_set_generator {
	my ($set_size, $x) = @_;
	my @list;
	my @students = glob("$students_dir/*");
	$x = min(max($x, 0), $#students);

	if((($#students)-$x) < $set_size) {	
		$set_size = $#students-$x+1;
	}

	for($i = 0; $i < $set_size; $i++){
		my $student_to_show  = $students[$x+$i];
		
		if($debug) {
			print " $i ($x):";
			print " $student_to_show ";
		}
		$list[$i] = $student_to_show;
	}
	return (@list);
}

# checks the password to see if it correct returns fail flag = 0 so an failed login message may pop up.
sub check_login {
	my $username = param('username');
	my $password = param('password');

	$fail = 0;
	$success = 1;

	$student_path = "./students/$username";
	my $profile_file = "$student_path/profile.txt";
	open my $p, "$profile_file" or return $fail;
	while (<$p>) {
		if ($_=~/^[a-z]+_*[a-z]*:/) {
			if ($_=~/^password:/) {
				while(<$p>) {
				last if $_ !~/^\s/;
				$user_password = $_;
				}
				redo;
			}
		}
	} 
	
	$user_password =~ s/\W//g;

	if ($password eq $user_password) {
		return $success;
	} else {
		return $fail;
	}
}

sub index_screen {

	# $action stores what happened in the last script run. This tells the index screen where
	# it was triggered from e.g. from itself (next button or previous button) or from loggin page.
	# $set_size tells the program how many profiles to display.	
	
	my ($action) = @_ or "None";
	my ($set_size) = param('sample_size_number') || 10; # where 10 is determines how many profiles to be displayed on index_page.
														# Param('sample_size_number') was not implementated due to time and no marks awarded for.

	@student_usernames;
	@student_paths;

	# $profile_index_number tells the program where we are in playing the profiles e.g. we have 50 profiles and we are at 
	# 20~30 profiles in (meaning we displaying $set_size amounts which is 10).
	# action_logged_in tells the index_screen that it is the first time its ran adjusts $profile_index_number
	# action_next tells the index_screen that the previous run was from index_Screen and is ordering index_screen to display
	# the next 10 profiles
	# action_previous tells the index_screen to display the previous 10 profiles. action_previous has a if statement to guard against 
	# end-cases such as when we are on index_number 0 we can not go previous.
	# action_back tells the index_screen to display the same page we were before browsing someones profile
	# action_search tells the index_screen to display the search results.

	if ($action eq 'action_logged_in') {
		$profile_index_number = 0;
	} elsif ($action eq 'action_next') {
		$profile_index_number = param('index_profile_number') + $set_size;
	} elsif ($action eq 'action_previous') {
		if (param('index_profile_number') > 0) {
			$profile_index_number = param('index_profile_number') - $set_size;
		} else {
			$profile_index_number = 0;
		}
	} elsif ($action eq 'action_back') {
		$profile_index_number = param('index_profile_number');
	} elsif ($action eq 'action_search') {
		# This was done due to bugging out when index_page was first loaded from the log-in page
		# It would bug out due to param('index_profile_number') not existing
		if(!defined param('index_profile_number')) {
			$profile_index_number = 0; 
		} else  {
			$profile_index_number = param('index_profile_number');
		}
		# search_profile_function just searches the input from param('search_profile')
		# param('search_profile') a string from user input.  
		$profile_found = search_profile_function(param('search_profile'));
	} 

	# display_set_generator goes through the profiles in ./students and fetches the data in a format
	# it will then return it in an array.
	my (@display_profiles) = display_set_generator($set_size, $profile_index_number); 

	foreach $student (@display_profiles) {
		$student_username = $student;
		$student_username =~ s/.\/students\///;
		push @student_usernames, $student_username;
		$profile_path = $student;
		push @student_paths, $profile_path;
	}
	
	# What each of the variables past to INDEX_SCREEN_HTML is detailed at the subroutine.
	index_screen_html ($set_size , $profile_index_number, $profile_found,\@student_usernames, \@student_paths);
	
}

sub browse_screen {
	my ($student_to_show) = @_;

	# This is where we exact the data from the profile.txt and store it in a string
	# This is also where we dis-include any data which is sensitive
 
	my $profile_file_name = "$student_to_show/profile.txt";
	open my $p, "$profile_file_name" or die "can not open $profile_file_name: $!";
	while (<$p>) {
		if ($_=~/^[a-z]+_*[a-z]*:/) {
			if (($_!~/^name:/) 
			&& ($_!~/^email:/) 
			&&	($_ !~/^password:/) 
			&& ($_ !~/^courses:/)) {
				chomp $_;
				$profile .= "cat:$_";
				while(<$p>) {
					last if $_ !~/^\s/;
					chomp $_;
					$profile .= " value=$_";
				}
				redo;
			}
		}
	} 
	
	close $p;

	# This is where format the data in to a hash. 
	# This is done to allow the HTML generation page "profile_screen_html()" 
	# to take data only needed e.g. if we only need degree or username we can just use the data_hash.
	
	%data_hash = ();
	@profile_data = split ("cat:", "$profile");
	foreach (@profile_data) {
		$cat_title = $_;
		$cat_title =~ s/:.*//g;
		#print "<br>cat_title = $cat_title<br>";
		chomp $_;
		#print $_;
		if ($_ =~ /$cat_title:/) {
			$_ =~ s/$cat_title://;
			$_ =~ s/\s*value=\s*/<p>/g;
			$_ =~ s/\n//;
			$cat_title =~ s/_/ /g;
			$data_hash{"$cat_title"}=$_;
		}
	}

	$profile_image_name = "$student_to_show/profile.jpg";
	$hidden_variable = param('index_profile_number');

	return profile_screen_html($student_to_show, $data_hash);
}

 #============HTML========================================================================================================================
	# THESE SUBROUTINES MOSTLY GENERATE HTML AND DOES MINIMAL WORK ON DATA PROCCESSING
	# Comment from coder: Yes I should have used templates, I happen to run out of time.
	# and yes I will in future use templates and multiple files to seperate the functions of the code.
	
sub login_screen_html {

	# $fail_login_message contains a string which is to be printed in the event of failing to log in.
	my($fail_login_message) = @_ or "";

	print header;
	print "<html>\n";
	print "<head>\n";
	print "\t<title>CUPID ONLINE</title>\n";
	print "</head>\n";
	print "<body style=\"background-color:lightgrey\">\n";
	print "\t<h1 style=\"text-align:center\">CUPID</h1>\n";
	print "\t<i><h2 style=\"text-align:center\">Welcome to Cupid</h2></i><br>\n";
	print "<form method=\"POST\">\n";
	print "\t<center><b>Username</b><center><br>\n";
	print "\t<center><input style=\"text-align:center\" type=\"text\" name=\"username\"></center><br>\n";
	print "\t<center><b>Password</b><center><br>\n";
	print "\t<center><input style=\"text-align:center\" type=\"password\" name=\"password\"></center><br>\n";
	print "<input type=\"submit\" name=\"login_button\" value=\"Login\">\n";
	print "</form>\n";

	# This part is only used when displaying a failed login message during the log in phase.

	if ($fail_login_message eq "") {
		print "\t<center><p style=\"color:red;font-size:80%\">$fail_login_message</p><center>\n";
	}
	print "</body>\n";
	print "</html>";
	
}


#	Subroutine to print out the HTML for the index page
sub index_screen_html () {

	# $set_size means how many profiles are to be displayed on the index
	# $profile_index_number tells us where we are up to in displaying the students. 
	# $profile_found is a string used for the search function - MORE DETAIL IS EXPLAINED
	# $student_usernames is an array which contain all the usernames of the students
	# $student_paths is an array which contains all the path names of the students
	my ($set_size, $profile_index_number, $profile_found, $student_usernames, $student_paths) = @_;

	$x = $profile_index_number;	

	print header;
	print "<head>\n";
	print "<style>\n";
	print "table, th, td {\n";
    print "\tborder: 1px solid black;\n";
	print "\tborder-collapse: collaspe;\n";
	print "}\n";
	print "td {\n";
	print "\tpadding: 5px;\n";
	print "\ttext-align: center;\n";
	print "</style>\n";
	print "\t<title>CUPID ONLINE</title>\n";
	print "</head>\n";
	print "<body style=\"background-color:lightgrey\">\n";
	print "\t<h1 style=\"text-align:center\">CUPID</h1>\n";
	print "\t<br>\n";
	print "\t<i><h2 style=\"text-align:center\">Search</h2></i>\n";
	print "\t<br>\n";
	print "<form method=\"POST\">\n";

	print "\t<center>\n<input style=\"text-align:center\" type=\"text\" name=\"search_profile\"><br>\n";
	print "\t<button type=\"submit\" name=\"search_button\" value=\"\">Search Profile</button><br>\n";

	# This part of the HTML / CODE is to generate the appropiate response for the search button
	# IF $profile_found = not_found string; it means the profile doesn't exist.
	# IF $profile_found = empty string; it means that the user press search button without entering in anything.
	# IF $profile_found is none of the above it means we found the user

	if (defined param('search_button')) {
		if($profile_found eq "not_found") {
			print "\t<p style=\"color:red\">user not found</p>\n";
		} elsif ($profile_found eq "empty") {
			print "\t<p style=\"color:red\">nothing has been entered</p>\n";
		} else {
			$p = param('search_profile');
			print "\t<br>\n";
			print "\t<h4>Your Search Result</h4>\n";
			print "\t<div style=\"width:300px;height:300px;border:1px solid black;\">\n";
			print "\t<img src=\"./students/$p/profile.jpg\"style=\"width:50%;height:50%\">\n";
			print "\t<p>Username: $p</p>\n";
			print "\t<button type=\"submit\" name=\"view_profile_button\" value=\"./students/$p\">View Profile</button>\n";
			print "\t</div>\n";
		} 
	} else  {
		print "<br>\n";
	}

	print "\t</center>\n";
	print "\n<br><br><br>\n";
	print "\t<i><h2 style=\"text-align:center\">Your selections today</h2></i><br>\n";

	print "<table align=\"center\" style=\"width:60%\">\n";

	#looping through the students and printing out HTML to display their display_pictures and username with a submit to get more information of that person.
	for ($i = 0; $i <= $#student_paths; $i++) {
		print "\t<tr>\n";
		print "\t\t<td ><img src=\"$student_paths[$i]/profile.jpg\" style=\"width:70%;height:80%\"></td>\n";
		print "\t\t<td>$student_usernames[$i]\n";
		print "\t\t</td>\n";
		print "\t\t<td><button type=\"submit\" name=\"view_profile_button\" value=\"$student_paths[$i]\">View Profile</button></td>\n";
		print "\t</tr>\n";
	}

	print "</table>\n";
	print "<br><br>";
	print "<table align=\"center\" style=\"width:100\">\n";
	print "\t<tr>\n";
	print "\t\t<td><button type=\"submit\" name=\"prev_button\" value=\"$set_size\">Previous</button></td>\n";

	# $y is the upper number displayed on the bottom of the index e.g. 0 ~ $y which is 0 ~ 10 or 10 ~ 20.
	# + 1 because the $#student_paths gives us 9 due to the nature of arrays.
	$y = $x+$#student_paths+1;

	print "\t\t<td>$x-$y</td>\n";
	print "\t\t<td><button type=\"submit\" name=\"next_button\" value=\"$set_size\">Next</button></td>\n";
	print "\t<tr>\n";
	print "</table>\n";	
	print "<br><br>\n";
	print "\t<center><input type=\"submit\" name=\"logout_button\" value=\"Logout\"></center>\n";
	print "\t<input type=\"hidden\" name=\"index_profile_number\" value=\"$x\"><br>\n";

	print "</form>\n";
	print "</body>\n";
	print "</html>\n";

}

# Subroutine for the HTML generation of  a profile page of a student.
sub profile_screen_html {

	my ($username, $data_hash) = @_;
	
	#This LIST of keys for the hash which has all the student data.
	@data_order = ('gender','degree','favourite movies','favourite bands','favourite hobbies','favourite books','birthdate','hair colour','height','weight');

	if ($username eq "") {
		$username = "default";
	}

	print header;
	print "<head>\n";
	print "\t<title>CUPID ONLINE</title>\n";
	print "</head>\n";
	print "<body style=\"background-color:lightgrey\">\n";
	print "\t<h1 style=\"text-align:center\">CUPID</h1>\n";
	print "\t<i><h2 style=\"text-align:center\">$data_hash{'username'}\'s profile page</h2></i><br>\n";
	print "\t<center><img src=\"$username/profile.jpg\" style=\"width:30%;height:50%\"></center>\n";
	print "\t<br><br>\n";
	print "<table border=\"1\" style=\"margin:0px auto; width:500px\">";	

	#This is responsible for the student's data e.g. username, weight, gender, degree, etc
	foreach $cat (@data_order) {
		
		print "\t<tr>\n";
		print "\t\t<td align=\"char\">$cat</td>\n";
		print "\t\t<td>$data_hash{$cat}</td>\n";
		print "\t</tr>\n";
	}

	print "</table>\n";

	print "<br><br>\n";
	print "<form method=\"POST\">";
	print "\t<center><button type=\"submit\" name=\"back_button\" value=\"Back\">Back to matches</button></center>\n";

	#$x is the index profile number which tells us which students to generate once, the index page is loaded again.
	$x = param('index_profile_number');

	print "\t<input type=\"hidden\" name=\"index_profile_number\" value=\"$x\"><br>\n";
	print "</form>\n";
	print "</body>\n";
	print "</html>\n";
}

# HTML TRAILERS
sub page_trailer {
	my $html = "";
	$html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
	$html .= end_html;
	return $html;
}


