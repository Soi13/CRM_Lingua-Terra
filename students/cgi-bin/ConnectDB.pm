package ConnectDB;
use strict;
use DBI;
#use CGI::Carp qw(fatalsToBrowser);

sub connect {
	my $dbh=DBI->connect("DBI:mysql:spending", "root", "") or die "Error: $DBI::errstr\n";
	return $dbh;
	}
1;
