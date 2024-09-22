#!/Perl64/bin/perl -w
use strict;
use DBI qw(:sql_types);
use CGI;
use CGI qw (:standart);
use CGI qw(:cgi);
use CGI::Carp qw(fatalsToBrowser);
use JSON;
use ConnectDB;
use CGI::Session;
use Encode;

my $SID;
my $method;

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');


my $cgi=CGI->new;
my @res;


#Определяем наименование группы и стоимость курса
my $data;
my $dbh=ConnectDB->connect; #Используем модуль ConnectDB для подключения к БД
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select SUMM_4_OPL from pays where ID=10544";
$sth=$dbh->prepare($sql);
$sth->execute();
my @row_dat = $sth->fetchrow_array;
#################################################


  my $op=JSON->new->pretty(1);
  #my $json=$op->encode(@res);
  my $json=$op->encode({result => sprintf("%.2f",  $row_dat[0])});

  print $cgi->header(-type=>"application/json", -charset=>"windows-1251");
  print $json;





__END__
