#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
# some globals used through the script
$debug = 1;
$students_dir = "./students";

#This is where all the magic happens ===========================================================================

print page_header();

	print "Restarted Script";
	$login_state = param('login');

if (defined param('press_action')) {

	print h2("INSIDE PROFILE");
	print h2("action pressed");
	$profile_selected = param('press_action');
	print browse_screen($profile_selected);

} elsif ((defined param('login') && $login_state eq "login") || defined param('back_button')) {

	#displau_profiles will contain all the profiles to be displayed on the main_index_screen. Default set size = 6.
	my (@display_profiles) = display_set_generator(6); 
	main_index_screen(@display_profiles);

} elsif (defined param('username')) {
	print h2("in username");
	print start_form;
	print br(), "\n";
	print center('Username: ', textfield('username', '' , 20));
	print center('Password: ', password_field('password','',20));
#	print param('login', $login_state);
#	print param('username', $username);
#	print param('password', $password);
#	print hidden('login');
#	print hidden('username');
#	print hidden('password');

	if(defined param('login')) {
		print h2('LOGIN DEFINED'); 
	} 
	if($login_state eq 'login') {
		print h2('LOGIN is correct');
	}

	if (check_login(param('username'))) {
		#print hidden('username');
		#print hidden('password');
		$login_state = "login";
		#$login_state = 1;
	} else {
		print center(h2("username or password not correct"));
		$login_state = "false";
	}

	print center(submit ('login'));
	print end_form;

} elsif (!defined param('username') || !defined param('password') || !defined param('login')) {
	print h2("in login");
	#login page

	print start_form;
	print br(), "\n";
	print center('Username: ', textfield('username', '' , 20));
	print center('Password: ', password_field('password','',20));
	print center(submit ('login'));
	print param('login', $login_state);
	print param('username', $username);
	print param('password', $password);
	print hidden('login', 'false');
	print hidden('username');
	print hidden('password');
	print end_form;

} else {
	print center(h2("ops error occurred"));
}

print page_trailer();

#==========================================================================================================================

if($debug) {
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
}

exit 0;	



sub check_login {
	my $username = param('username');
	my $password = param('password');

	#print $username;
	#print $password;

	$fail = 0;
	$success = 1;

	$student_path = "./students/$username";
	my $profile_file = "$student_path/profile.txt";
	open my $p, "$profile_file" or return $fail;
	while (<$p>) {
		if ($_=~/^[a-z]+_*[a-z]*:/) {
			if ($_=~/^password:/) {
				#$user_password = $_;
				while(<$p>) {
				last if $_ !~/^\s/;
				$user_password = $_;
				}
				redo;
			}
		}
	} 
	
	#print $user_password;
	$user_password =~ s/\W//g;

	if ($password eq $user_password) {
		return $success;
	} else {
		return $fail;
	}
}

#display_set_generator takes in a integer which serves as the number of students that are to be displayed on main_index_screen.
#Input : Integer (default set to 6) 
#Output: list student path names (Path names are to their account information e.g. with profile.txt and profile.jpg)
#STUFF TO DO: Impliment a stopper which stops before the end of the array
#Stuff to do: impliement a inintalise point so that when we have a previous button it will
#grey-out the previous if we are on the first set e.g. index 0. 
sub display_set_generator {
	my ($set_size) = @_;
	my @list;
	my $x = param('x') || 0;
	my @students = glob("$students_dir/*");
	$x = min(max($x, 0), $#students);
	param('x', $x + $set_size);
	for($i = 0; $i < $set_size; $i++){
		my $student_to_show  = $students[$x+$i];
		if($debug) {
			print " $i ($x):";
			print " $student_to_show ";
		}
		$list[$i] = $student_to_show;
	}
	#print " Inside loop finish \n";
	return (@list);
}

sub main_index_screen {
	my (@students_to_display) = @_;
	print h2("Index Page");
	print start_form, "\n";
	foreach $student (@students_to_display) {
		$profile_icon = "$student/profile.jpg";
		$student_username = $student;
		$student_username =~ s/.\/students\///;

		print img({src=>$profile_icon, width=>'20%', height=>'30%'}), "\n";
		print br(),"\n";
		print submit("press_action", $student_username),"\n"; #To make name text clickable use CSS
		#print hidden($student_username, $student);
		print hr(),"\n";
		
		if($debug) {
			print "main_index_screen: $student_username\n";
			print "debug: profile_icon path is $profile_icon\n";
		}
	}
	print end_form, "\n";
}

#TODO: WE need to finish of the logic, We need to finish off linking each name/icon to display their profiles, We need to finish off login, lastly figure out how to make it look nice (CCS MAYBE?)

sub browse_screen {
	my ($student_to_show) = @_;
	$student_to_show = "./students/$student_to_show";
	my $profile_file_name = "$student_to_show/profile.txt";
	open my $p, "$profile_file_name" or die "can not open $profile_file_name: $!";
	#$profile = join '', <$p>;
	while (<$p>) {
		if ($_=~/^[a-z]+_*[a-z]*:/) {
			if (($_!~/^name:/) 
			&& ($_!~/^email:/) 
			&&	($_ !~/^password:/) 
			&& ($_ !~/^courses:/)) {
				$profile .= $_;
				while(<$p>) {
				last if $_ !~/^\s/;
				$profile .= $_;
				}
				redo;
			}
		}
	} 
	
	close $p;
	
	#SUBSET0 - Hiding Private information of each member: 
	#1) Real Name 2) email 3) password 4) courses taken.	


	#SUBSET0 - displaying profile image

	$profile_image_name = "$student_to_show/profile.jpg";
	#open my $p_image, "$profile_image_name" or die "can not open $profile_image_name: $!";
	#$profile_image_name = "$profile_image_name"."profile.jpg";
	#print "$profile_imagename";
	#print "<img src='$profile_image_name' width='25%' height='25p%' + />";
	#close $p_image;

	#SUBSET1 - Creating a main page



	return p,		
		start_form, "\n",
		img({src=>$profile_image_name,width=>'10%', height=>'25%'}),"\n",
		pre($profile),"\n",
		hidden('n', $n + 1),"\n",
		hidden('x', $x + 6),"\n", #Detele later when generate is done.
		submit('back_button','Back to your selections'),"\n",
		end_form, "\n",
		p, "\n";
}

#
# HTML placed at bottom of every screen
#
sub page_header {
	return header,
		start_html(
					-title => 'Cupid Online',
					-bgcolor => 'grey',
					),"\n",
		center(h2('CUPID')),"\n";
 #  		start_html("-title"=>"LOVE2041", -bgcolor=>"#FEDCBA"),
	#	"<link rel='stylesheet' href='styles.css'>"
 	#	center(h2(i("LOVE2041")));
}

#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
	my $html = "";
	$html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
	$html .= end_html;
	return $html;
}
