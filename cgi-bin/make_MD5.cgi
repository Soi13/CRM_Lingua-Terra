#!/Perl64/bin/perl -w
use DBI;
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
use CGI::Carp qw(fatalsToBrowser);
use Digest::MD5 qw(md5_hex);

my $n=md5_hex("EwHf#!45*Jkg");


print "Content-type: text/html\n\n";
print "<html><h1>$n</h1></html>\n";



__END__