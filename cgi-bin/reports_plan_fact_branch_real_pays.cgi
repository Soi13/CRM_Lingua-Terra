#!/Perl64/bin/perl -w
use strict;
use DBI;
use CGI;
#use CGI::Carp qw(fatalsToBrowser);
use CGI qw(:standart);
use CGI::Session;
use CGI qw(:cgi);
use Digest::MD5 qw(md5_hex);
use Build_Menu qw(:DEFAULT $idd);

my $SID;
my $method;

if (defined(cookie('SID'))) {
        $SID=cookie('SID');
		$SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='cookies';
        }
elsif (defined(param('SID'))) {
        $SID=param('SID');
        $SID=~s/\0//g; $SID=~s/\.\.//g; $SID=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        $method='path';
        }
else {
        print "Location: http://localhost:6080\n\n";
        exit();
        }

my $sess=CGI::Session->new("driver:mysql", $SID, {DataSource=>"dbi:mysql:spending",User=>"root", Password=>""}) or die CGI::Session->errstr();
$sess->name('SID');

#���� ������ ������
if ($sess->is_empty()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� ����� ������ �������
if ($sess->is_expired()) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#���� IP �� ���������
if ($sess->remote_addr() ne $ENV{'REMOTE_ADDR'}) {
        &f_delete_session();
        print "Location: http://localhost:6080\n\n";
        exit();
        }

#����������� ���������� ����� � ������ ������������ �� ������
my $formLogin=$sess->param('Login');
my $formPass=$sess->param('Password');
my $PLAN_FACT_REAL_PAYS_MONTH_REPORTS=$sess->param('PLAN_FACT_REAL_PAYS_MONTH_REPORTS');

#������� ���������� �� ����� � ������ ������������ � �����
if (defined($formLogin) && defined($formPass)) {

    if ($PLAN_FACT_REAL_PAYS_MONTH_REPORTS==1) #������� ����� �� ������ ������������ � ������ ����-���� �������� �����������.
    {

        #���������� �������� ����������� ��� ������ �� �� ��������
        open FF, "<txt_data/name_org.txt";
        my @name_org=<FF>;
        foreach my $str (@name_org)
        {
           $str=~s/\0//g;
           $str=~s/\.\.//g;
           $str=~s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
        }
        close (FF) or die $!;
        #########################################

        print "Content-type: text/html\n\n";
        print <<HTML;
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset='windows-1251'>
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>@name_org</title>
        <link rel="stylesheet" type="text/css" href="../CSS/easyui.css">
        <link rel="stylesheet" type="text/css" href="../CSS/icon.css">
        <link rel="stylesheet" type="text/css" href="../CSS/demo.css">
        <link rel="stylesheet" type="text/css" href="../CSS/dhtmlxscheduler.css">
        <link rel="stylesheet" href="../CSS/styles.css">
        <link rel="stylesheet" href="../CSS/multiline_scheduler.css">  
        <script type="text/javascript" src="../JS/jquery.min.js"></script>
        <script type="text/javascript" src="../JS/jquery.easyui.min.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler.js"></script>   
        <script type="text/javascript" src="../JS/locale_ru.js" charset="utf-8"></script>     
        <script type="text/javascript" src="../JS/dhtmlxscheduler_readonly.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_quick_info.js"></script>
        <script type="text/javascript" src="../JS/dhtmlxscheduler_active_links.js"></script> 
        <script type="text/javascript" src="../JS/datagrid-detailview.js"></script>        
        <script src="../JS/script.js"></script>
        <script src="../ckeditor/ckeditor.js"></script>
        <script src="../ckeditor/adapters/jquery.js"></script> 

        
        <script>
        function confirm1(){
        \$.messager.confirm('��������', '�� �������, ��� ���������� �����', function(r){
        if (r){
        //alert('confirmed: '+r);
        window.location.replace("/cgi-bin/exit.cgi?SID=$SID");
        }     });  }   </script>

        <!--Increae time of life session-->
        <script>
        \$(document).mouseup(function (e){
        \$.ajax({
                url: '/cgi-bin/session_alive.cgi?SID=$SID',
                success: function(){
                window.location.replace("http://localhost:6080")}
                                });  });    </script>

        <script> //�������� ����� ����� ������
        function call() {
        var msg   = \$('#ff').serialize();
        \$.ajax({
          type: 'GET',
          url: 'change_psw.cgi?SID=$SID',
          data: msg,
          success: function(res) {alert(res.result); \$('#ff')[0].reset(); \$('#w').window('close');},
          error: function() {alert("did not work");}
        });

       }
       </script>

                                                  
       <script>//��������� Keyboard Navigation
        \$(function(){
        \$('#dg').datagrid('getPanel').panel('panel').attr('tabindex',0).bind('keydown',function(e){
	switch(e.keyCode){
		case 38:	// up
			var selected = \$('#dg').datagrid('getSelected');
			if (selected){
				var index = \$('#dg').datagrid('getRowIndex', selected);
				\$('#dg').datagrid('selectRow', index-1);
			} else {
				\$('#dg').datagrid('selectRow', 0);
			}
			break;
		case 40:	// down
			var selected = \$('#dg').datagrid('getSelected');
			if (selected){
				var index = \$('#dg').datagrid('getRowIndex', selected);
				\$('#dg').datagrid('selectRow', index+1);
			} else {
				\$('#dg').datagrid('selectRow', 0);
			}
			break;
	}
       });
       });
       </script>
       
       <script>
       \$(function(){
        var img = '<img src="../images/Excel.ico" style="width:20px;height:20px;align:left">';
        var txt = '<span style="line-height:21px;">������ � Excel</span>';
        \$('#excel').linkbutton({
                             text: img+txt
                            })
        });
        </script>
        
                
        <script>
        function make_report() {
          var mth=\$('#month').combobox('getValue');
          var yr=\$('#year').combobox('getValue');
          \$.ajax({            
                         type: 'POST',
                         traditional: true,
                         url: 'get_plan_fact_branches_real_pays.cgi',
                         data: {'month':mth, 'year':yr, 'SID':'$SID'},            
                         success: function(res) {                                              
                                                 \$('#dg').datagrid('loadData', res.rows).datagrid('reloadFooter', res.footer);                                                 
                                                },
                         error: function() {alert("did not work");}
                  });
                     
         }
        </script>
        
        
        <script>
        \$(function(){
           var dt= new Date();
           \$('#year').combobox('setValue', dt.getFullYear());                               
        });
        </script>
        
        
        <script>
        \$(function(){
            \$('#dg').datagrid({
                view: detailview,
                detailFormatter:function(index,row){
                    return '<div style="padding:2px"><table class="ddv"></table></div>';
                },
                onExpandRow: function(index,row){
                    \$('#dg').datagrid('selectRow',index);
                    var row_br = \$('#dg').datagrid('getSelected'); 
                    var ddv = \$(this).datagrid('getRowDetail',index).find('table.ddv');                    
                    ddv.datagrid({
                        url:'get_plan_fact_branches_real_pays_detail_teachers.cgi?SID=$SID&id_br='+row_br.br_id+'&per='+row_br.period,
                        method: 'get',
                        fitColumns:true,
                        singleSelect:true,
                        rownumbers:true,
                        loadMsg:'',
                        height:'auto',
                        columns:[[
                            {field:'teacher',title:'�������������',width:90},
                            {field:'fact',title:'����',width:100,align:'right'}                            
                        ]],
                        onResize:function(){
                            \$('#dg').datagrid('fixDetailRowHeight',index);
                        },
                        onLoadSuccess:function(){
                            setTimeout(function(){
                                \$('#dg').datagrid('fixDetailRowHeight',index);
                            },0);
                        }
                    });
                    \$('#dg').datagrid('fixDetailRowHeight',index);
                  
                }
            });
        });
        </script>
     
        </head>
        <body class="easyui-layout">
        <!--������� DIV - ��������� -->
        <div data-options="region:'north',border:false" style="height:100px;background:#f0993c;padding:10px;"><h1 class="shd">@name_org</h1>
        <!--DIV � ������� ����� ������ ������-->
HTML
     
        #���������� ������, ������� ����� �� ������� ������
        open FF1, "<txt_data/buttons_panel.txt";
        my @buttons_panel=<FF1>;
        foreach my $str_but (@buttons_panel)
        {
           $str_but=~s/\0//g;
           $str_but=~s/\.\.//g;
           $str_but=~s/[<]*script[^>]*>.*[<]*\/script[>]*//i; #�� ���� ������ ������� ���� <script>
		   $str_but=~s/SID=\$SID/SID=$SID/i; #����������� ���������� ���� SID � ������ ������ ���������� $SID. ��� �� �� �������������, �.�. ������ �������� �� ���������� �����.
        }
        close (FF1) or die $!;        
        print @buttons_panel;
        ######################################### 
        
        print <<HTML1;
        <!--����� DIV � ������� ����� ������ ������-->
        </div>
        <!--����� ������� DIV - ��������� -->

        <!--����� DIV ������ ���� -->
        <div data-options="region:'west',split:false,title:'����'" style="width:205px;">

        <div id='cssmenu'>
        <ul>
HTML1
        #���������� � ��������� ����
        my $us_id=$sess->param('USER_ID'); #������ �� ������ USER_ID
        Build_Menu->menu($us_id, $SID); #� �������� ������� ��������� ID ������������ ��� ������ ����
        print <<HTML_e;
        </ul>
        </div>

        </div>
        <!--����� ����� DIV ������ ���� -->

        <!-- ������ DIV ������ ����������� -->
        <!-- <div data-options="region:'east',split:true,title:'�����������'" style="width:30%;padding:1px;"> -->
        <!-- </div> -->
        <!-- ����� ������ DIV ������ ����������� -->

        <!--<div data-options="region:'south',border:false" style="height:50px;background:#A9FACD;padding:10px;">south region</div>-->

        <!-- ����������� DIV -������� ������� -->
        <div data-options="region:'center',title:'������� ������� - ����� - �������� ����������� �� ����� �� ��������. ������������: $formLogin'">

        <table id="dg" title="�������� ����������� �� ����� �� ��������" class="easyui-datagrid" style="width:100%;height:95%"
        method="get"
        url=""
        toolbar="#tb"
        rownumbers="true" fitColumns="true" singleSelect="true" sortName="nm_dg" sortOrder="asc" showFooter="true">

        <thead>
        <tr>
            <th field="br_id" width="15" hidden="true">br_id</th>
            <th field="br" width="150" sortable="true">������</th>
            <th field="fact" width="167">����</th>
            <th field="period" width="167" hidden="true">period</th>                                    
        </tr>
        </thead>
        </table>        
              
        <!-- ������ ������ -->
        <div id="tb" style="padding:3px">
             <div style="margin-top:5px; margin-bottom:5px">
               <span>������������ ����� �� �����:</span>
               <select id="month" class="easyui-combobox" name="month" style="width:100px" data-options="editable:false">
               <option value="1">������</option>
               <option value="2">�������</option>
               <option value="3">����</option>
               <option value="4">������</option>
               <option value="5">���</option>
               <option value="6">����</option>
               <option value="7">����</option>
               <option value="8">������</option>
               <option value="9">��������</option>
               <option value="10">�������</option>
               <option value="11">������</option>
               <option value="12">�������</option>             
               </select>

               <span>    ���:</span>
               <select id="year" class="easyui-combobox" name="year" style="width:100px" data-options="editable:false">
               <option>2016</option>
               <option>2017</option>
               <option>2018</option>
               <option>2019</option>
               <option>2020</option>
               <option>2021</option>
               <option>2022</option>
               <option>2023</option>
               <option>2024</option>
               <option>2025</option>
               <option>2026</option>
               <option>2027</option>             
               </select>

               <a href="#" class="easyui-linkbutton" plain="false" onclick="make_report()" style="border-radius:5px; width:100px;">������������</a>             
               <a id="excel" href="#" class="easyui-linkbutton" plain="true" onclick="javascript:alert('������ ������� � ����������')" style="float:right">Excel</a>
             </div>                       
        </div>
        <!-- ����� ������ ��� ������ -->

        </div>
        <!-- ����� ����������� DIV -������� ������� -->

        <!-- ����� ��������� ������ -->
        <div id="w" class="easyui-window" title="����� ������" data-options="modal:true,closed:true,iconCls:'icon-save'" style="width:370px;height:170px;padding:10px;">
        <form id="ff" action="javascript:void(null);" onsubmit="call()" method="post" enctype="multipart/form-data">
            <table>
                <tr>
                    <td>������� ������:</td>
                    <td><input id="curr_psw" name="curr_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>����� ������:</td>
                    <td><input name="new_psw" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>��� ���:</td>
                    <td><input name="new_psw1" type="password" class="f1 easyui-textbox"></input></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <td></td>
                    <td><input type="submit" value="�����������"></input></td>
                </tr>
            </table>
        </form>
    </div>
    <!-- ����� ����� ��������� ������ -->
           
        </body>
        </html>
HTML_e

        #���������� ����� ����� ������
        $sess->atime(time());
        $sess->flush();

  } 
  else
  {
       &f_delete_session(); #������� ������
       
       print "Content-type: text/html\n\n";
       print <<HTML3;
       
       <!doctype html>
       <html>
       <head>
       <meta charset="windows-1251">
       <title>��� �������</title>

       <script type="text/javascript">
       setTimeout('location.replace("http://localhost:6080")', 3000);
       </script>

       <noscript>
       <meta http-equiv="refresh" content="3; url=http://localhost:6080">
       </noscript>

       <style type="text/css">
       body {
	       background-color: #4E5869;
       }
       .zagolovok {
	            font-family: "Times New Roman", Times, serif;
	            color: #FF0;	
       }
       </style>
       </head>

       <body>
       <h1 align="center" class="zagolovok"><strong>� ��� ��� ������� � ������� ������!</strong></h1>
       </body>
       </html>       
HTML3
   } 

#�������� ������
sub f_delete_session {
         #������� ����
         my $cookies=cookie(-name=>$sess->name(), -value=>'', -expires=>'-1d', -path=>'/', -domain=>'http://localhost:6080');
         print "Set-Cookie: $cookies\n";
         #������� ������
         $sess->delete();
         $sess->flush();
        }

#���������� SID � URL-������
sub f_add_sid {
        my $url=shift();
        if ($method eq 'path') {
                if (defined($SID) && $url !=~ m/SID=/) {
                        if ($url !=~ m/\?/) {
                                $url.="?SID=".$SID;
                                }
                        else {
                                $url.="&SID=".$SID;
                             }
                        }
                }
                return $url;
              }

}
else { print "Location: http://localhost:6080\n\n"; }