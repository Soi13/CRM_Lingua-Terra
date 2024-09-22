#!/usr/bin/perl

#use strict;
use DBI;

my $dbh = DBI->connect(          
    "dbi:mysql:dbname=a0018982_fin", 
    "a0018982_oleg",                          
    "",                          
    { RaiseError => 1 },         
) or die $DBI::errstr;

my $sth = $dbh->prepare("select SUMM_4_OPL from pays where ID=10544");
$sth->execute();

my $row;
while ($row = $sth->fetchrow_arrayref()) {
    print "@$row[0] @$row[1] @$row[2]\n";
}

$sth->finish();
$dbh->disconnect();
