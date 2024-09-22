package Build_Menu;
use strict;
use DBI;
use CGI::Carp qw(fatalsToBrowser);
use ConnectDB;
use Carp;
require Exporter;

my @ISA=qw(Exporter);
my @EXPORT=qw(menu);
my @EXPORT_OK=qw($idd, $SID);



sub menu
{

my @idd=@_; #� ���� ������ ����������� ID ����������� ���������� � ����������� �������, ID ����� � ������� �� ������ �������� ,�.�. � $idd[1]
my $data;
my $dbh=ConnectDB->connect;
my $sth=$dbh->do("SET NAMES 'cp1251'");
my $sql="select * from usr where ID like ?";
$sth=$dbh->prepare($sql);
$sth->execute($idd[1]); #ID ����� � ������� �� ������ �������� ,�.�. � $idd[1]

my @row = $sth->fetchrow_array; #��������� ������� ���������� � ������

$dbh->disconnect;
   
   ##################������ ���� �����������#################################
   if ($row[5]==1 && $row[6]==1 && $row[7]==1 && $row[8]==1 && $row[9]==1 && $row[10]==1 && $row[11]==1 && $row[12]==1 && $row[13]==1 && $row[14]==1 && $row[15]==1 && $row[16]==1 && $row[17]==1 && $row[47]==1 && $row[52]==1 && $row[58]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>�����������</span></a>
            <ul>
               <li><a href='sekretariat_main.cgi?SID=$idd[2]'><span>�������</span></a></li>
               <li><a href='sekretariat_groups.cgi?SID=$idd[2]'><span>������</span></a></li>
               <li><a href='sekretariat_students.cgi?SID=$idd[2]'><span>��������</span></a></li>
               <li><a href='sekretariat_teachers.cgi?SID=$idd[2]'><span>�������</span></a></li>
               <li><a href='sekretariat_rooms.cgi?SID=$idd[2]'><span>��������</span></a></li>
               <li><a href='sekretariat_calendar.cgi?SID=$idd[2]'><span>���������</span></a></li>
			   <li><a href='sekretariat_personal_calendar.cgi?SID=$idd[2]'><span>������ ���������</span></a></li>
               <li><a href='#'><span>�����</span></a></li>
               <li><a href='#'><span>�����</span></a></li>
               <li><a href='sekretariat_sms.cgi?SID=$idd[2]'><span>���</span></a></li>
               <li><a href='sekretariat_documents.cgi?SID=$idd[2]'><span>���������</span></a></li>
               <li><a href='#'><span>������������</span></a></li>
               <li><a href='sekretariat_zayavki.cgi?SID=$idd[2]'><span>������</span></a></li>
			   <li><a href='sekretariat_reserv.cgi?SID=$idd[2]'><span>������</span></a></li>
               <li class='last'><a href='#'><span>���������</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[5]==1 && ($row[6]!=1 || $row[7]!=1 || $row[8]!=1 || $row[9]!=1 || $row[10]!=1 || $row[11]!=1 || $row[12]!=1 || $row[13]!=1 || $row[14]!=1 || $row[15]!=1 || $row[16]!=1 || $row[17]!=1 || $row[47]!=1 || $row[52]!=1 || $row[58]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>�����������</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='sekretariat_main.cgi?SID=$idd[2]'><span>�������</span></a></li>\n) if ($row[6]==1);
         print qq(<li><a href='sekretariat_groups.cgi?SID=$idd[2]'><span>������</span></a></li>\n) if ($row[7]==1);
         print qq(<li><a href='sekretariat_students.cgi?SID=$idd[2]'><span>��������</span></a></li>\n) if ($row[8]==1);
         print qq(<li><a href='sekretariat_teachers.cgi?SID=$idd[2]'><span>�������</span></a></li>\n) if ($row[9]==1);
         print qq(<li><a href='sekretariat_rooms.cgi?SID=$idd[2]'><span>��������</span></a></li>\n) if ($row[10]==1);
         print qq(<li><a href='sekretariat_calendar.cgi?SID=$idd[2]'><span>���������</span></a></li>\n) if ($row[11]==1);
		 print qq(<li><a href='sekretariat_personal_calendar.cgi?SID=$idd[2]'><span>������ ���������</span></a></li>\n) if ($row[52]==1);
         print qq(<li><a href='#'><span>�����</span></a></li>\n) if ($row[12]==1);
         print qq(<li><a href='#'><span>�����</span></a></li>\n) if ($row[13]==1);
         print qq(<li><a href='sekretariat_sms.cgi?SID=$idd[2]'><span>���</span></a></li>\n) if ($row[14]==1);
         print qq(<li><a href='sekretariat_documents.cgi?SID=$idd[2]'><span>���������</span></a></li>\n) if ($row[15]==1);
         print qq(<li><a href='#'><span>������������</span></a></li>\n) if ($row[16]==1);
         print qq(<li><a href='sekretariat_zayavki.cgi?SID=$idd[2]'><span>������</span></a></li>\n) if ($row[47]==1);
		 print qq(<li><a href='sekretariat_reserv.cgi?SID=$idd[2]'><span>������</span></a></li>\n) if ($row[58]==1);
         print qq(<li><a href='#'><span>���������</span></a></li>\n) if ($row[17]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################������ ���� �������#################################
   if ($row[18]==1 && $row[19]==1 && $row[20]==1 && $row[21]==1 && $row[22]==1 && $row[23]==1 && $row[51]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>�������</span></a>
            <ul>
               <li><a href='#'><span>����������</span></a></li>
               <li><a href='#'><span>����-�������</span></a></li>
               <li><a href='finance_orders.cgi?SID=$idd[2]'><span>��������� ������</span></a></li>
               <li><a href='finance_import_from_bank.cgi?SID=$idd[2]'><span>������ ������ �� �����</span></a></li>
			   <li><a href='finance_export_2_bank.cgi?SID=$idd[2]'><span>������� ������ � ����</span></a></li>
               <li class='last'><a href='#'><span>���������</span></a></li>             
            </ul>
         </li>
HTML
   }
   elsif ($row[18]==1 && ($row[19]!=1 || $row[20]!=1 || $row[21]!=1 || $row[22]!=1 || $row[23]!=1 || $row[51]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>�������</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>����������</span></a></li>\n) if ($row[19]==1);
         print qq(<li><a href='#'><span>����-�������</span></a></li>\n) if ($row[20]==1);
         print qq(<li><a href='finance_orders.cgi?SID=$idd[2]'><span>��������� ������</span></a></li>\n) if ($row[21]==1);
         print qq(<li><a href='finance_import_from_bank.cgi?SID=$idd[2]'><span>������ ������ �� �����</span></a></li>\n) if ($row[22]==1);
		 print qq(<li><a href='finance_export_2_bank.cgi?SID=$idd[2]'><span>������� ������ � ����</span></a></li>\n) if ($row[51]==1);
         print qq(<li><a href='#'><span>���������</span></a></li>\n) if ($row[23]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################������ ���� �����������#################################
   if ($row[24]==1 && $row[25]==1 && $row[26]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>�����������</span></a>
            <ul>
               <li><a href='#'><span>���������</span></a></li>
               <li class='last'><a href='#'><span>���������</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[24]==1 && ($row[25]!=1 || $row[26]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>�����������</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>���������</span></a></li>\n) if ($row[25]==1);
         print qq(<li><a href='#'><span>���������</span></a></li>\n) if ($row[26]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################������ ���� E-LEARNING#################################
   if ($row[27]==1 && $row[28]==1 && $row[29]==1 && $row[30]==1 && $row[31]==1 && $row[32]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>E-learning</span></a>
            <ul>
               <li><a href='#'><span>�����</span></a></li>
               <li><a href='#'><span>��������</span></a></li>
               <li><a href='#'><span>����� �������</span></a></li>
               <li><a href='#'><span>�����</span></a></li>
               <li class='last'><a href='#'><span>����� ��������</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[27]==1 && ($row[28]!=1 || $row[29]!=1 || $row[30]!=1 || $row[31]!=1 || $row[32]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>E-learning</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>�����</span></a></li>\n) if ($row[28]==1);
         print qq(<li><a href='#'><span>��������</span></a></li>\n) if ($row[29]==1);
         print qq(<li><a href='#'><span>����� �������</span></a></li>\n) if ($row[30]==1);
         print qq(<li><a href='#'><span>�����</span></a></li>\n) if ($row[31]==1);
         print qq(<li><a href='#'><span>����� ��������</span></a></li>\n) if ($row[32]==1);         
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################
   
   
##################������ ���� ���������������#################################
   if ($row[33]==1 && $row[34]==1 && $row[35]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>���������������</span></a>
            <ul>
               <li><a href='#'><span>������ �������</span></a></li>
               <li class='last'><a href='#'><span>���������</span></a></li>               
            </ul>
         </li>
HTML
   }       
   elsif ($row[33]==1 && ($row[34]!=1 || $row[35]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>���������������</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>������ �������</span></a></li>\n) if ($row[34]==1);
         print qq(<li><a href='#'><span>���������</span></a></li>\n) if ($row[35]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################   


##################������ ���� �����������#################################
   if ($row[36]==1 && $row[37]==1 && $row[38]==1 && $row[39]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>����������</span></a>
            <ul>
               <li><a href='#'><span>�������</span></a></li>
               <li><a href='#'><span>�������������������</span></a></li>
               <li class='last'><a href='administration_tools.cgi?SID=$idd[2]'><span>���������</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[36]==1 && ($row[37]!=1 || $row[38]!=1 || $row[39]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>����������</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>�������</span></a></li>\n) if ($row[37]==1);
         print qq(<li><a href='#'><span>�������������������</span></a></li>\n) if ($row[38]==1);
         print qq(<li><a href='administration_tools.cgi?SID=$idd[2]'><span>���������</span></a></li>\n) if ($row[39]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################������ ���� ������#################################
   if ($row[40]==1 && $row[41]==1 && $row[60]==1 && $row[61]==1 && $row[62]==1 && $row[66]==1 && $row[68]==1 && $row[73]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>������</span></a>
            <ul>
               <li><a href='reports_debts_4_today.cgi?SID=$idd[2]'><span>�������� �� �������</span></a></li>
			   <li><a href='reports_debts_month.cgi?SID=$idd[2]'><span>�������� �� �����</span></a></li>
			   <li><a href='reports_plan_fact_branch.cgi?SID=$idd[2]'><span>����-���� �� �������� (�� ������)</span></a></li>
			   <li><a href='reports_plan_fact_branch_real_pays.cgi?SID=$idd[2]'><span>�������� ����������� �� ����� �� ��������</span></a></li>
			   <li><a href='reports_students_teachers.cgi?SID=$idd[2]'><span>��������/�������������</span></a></li>
			   <li class='last'><a href='reports_students_age.cgi?SID=$idd[2]'><span>�������� �� ��������</span></a></li>
			   <li class='last'><a href='reports_students_dogovors.cgi?SID=$idd[2]'><span>��������/��������</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[40]==1 && ($row[41]!=1 || $row[60]!=1 || $row[61]!=1 || $row[62]!=1 || $row[66]!=1 || $row[68]!=1 || $row[73]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>������</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='reports_debts_4_today.cgi?SID=$idd[2]'><span>�������� �� �������</span></a></li>\n) if ($row[41]==1);
		 print qq(<li><a href='reports_debts_month.cgi?SID=$idd[2]'><span>�������� �� �����</span></a></li>\n) if ($row[60]==1);         
		 print qq(<li><a href='reports_plan_fact_branch.cgi?SID=$idd[2]'><span>����-���� �� �������� (�� ������)</span></a></li>\n) if ($row[61]==1);
		 print qq(<li><a href='reports_plan_fact_branch_real_pays.cgi?SID=$idd[2]'><span>�������� ����������� �� ����� �� ��������</span></a></li>\n) if ($row[62]==1);         
		 print qq(<li><a href='reports_students_teachers.cgi?SID=$idd[2]'><span>��������/�������������</span></a></li>\n) if ($row[66]==1);
		 print qq(<li><a href='reports_students_age.cgi?SID=$idd[2]'><span>�������� �� ��������</span></a></li>\n) if ($row[68]==1);
		 print qq(<li><a href='reports_students_dogovors.cgi?SID=$idd[2]'><span>��������/��������</span></a></li>\n) if ($row[73]==1);  
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################


##################������ ���� E-������#################################
   if ($row[42]==1)
   {
      print qq (<li><a href='#'><span>E-������</span></a></li>);
   }
   ##########################################################################


##################������ ���� ����������#################################
   if ($row[43]==1)
   {
      print qq (<li><a href='#'><span>����������</span></a></li>);
   }
   ##########################################################################


##################������ ���� ������#################################
   if ($row[44]==1 && $row[45]==1 && $row[46]==1)
   {
         print <<HTML;
         <li class='has-sub'><a href='#'><span>������</span></a>
            <ul>
               <li><a href='#'><span>������</span></a></li>
               <li class='last'><a href='#'><span>��������</span></a></li>
            </ul>
         </li>
HTML
   }
   elsif ($row[44]==1 && ($row[45]!=1 || $row[46]!=1))
   {
         print qq(<li class='has-sub'><a href='#'><span>������</span></a>\n);
         print qq (<ul>\n);
         print qq(<li><a href='#'><span>������</span></a></li>\n) if ($row[45]==1);
         print qq(<li><a href='#'><span>��������</span></a></li>\n) if ($row[46]==1);
         print qq (</ul>\n);
         print qq (</li>\n);
   }
   ##########################################################################
}

__END__


