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
print page_header();

# some globals used through the script
$debug = 1;
$students_dir = "./students";

print browse_screen();
print page_trailer();
exit 0;	

sub browse_screen {
	my $n = param('n') || 0;
	my @students = glob("$students_dir/*");
	$n = min(max($n, 0), $#students);
	param('n', $n + 1);
	my $student_to_show  = $students[$n];
	my $profile_filename = "$student_to_show/profile.txt";
	open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
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
		h1("CUPID"),"\n",	
		start_form, "\n",
		img({src=>$profile_image_name,width=>'10%', height=>'25%'}),"\n",
		pre($profile),"\n",
		hidden('n', $n + 1),"\n",
		submit('Next student'),"\n",
		end_form, "\n",
		p, "\n";
}

#
# HTML placed at bottom of every screen
#
sub page_header {
	return header,
		start_html('CUPID'),"\n"
		#h2('CUPID'),"\n";
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
