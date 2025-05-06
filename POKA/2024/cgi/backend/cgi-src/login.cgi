#!/usr/bin/perl -w
 
use strict;
use warnings;
use DBI; 
use CGI;

my $q = CGI->new;

my $params_username = $q->param("username");
my $params_password = $q->param("password");

if($params_username && $params_password){

	my $conn_info = "DBI:mysql:database=testdb;host=mysql";
	my $conn_username = "root";
	my $conn_password = "password";

	my $conn = DBI->connect($conn_info, $conn_username, $conn_password, {
	    RaiseError => 1,
	    PrintError => 0,
	    AutoCommit => 1,
	}) or die "Could not connect to database: $DBI::errstr";

	my $sql = "SELECT * FROM users WHERE username=? and password=?";
	my $sth = $conn->prepare($sql);

	$sth->execute($params_username, $params_password);

	my ($res_user, $res_pass) = $sth->fetchrow_array();

	if($res_user && $res_pass){

		my $url = $q->param("url");

                if ($url =~ m{^https?://}) {
                        print "Location: $url";
                }else{
                        print "Content-Type: text/html\n\n";
                        print "<h3>Hello $res_user</h3>";
                }

		$sth->finish();
		$conn->disconnect();

	}else{
		print "Context-Type: text/html\n\n";
		print "<h3>?username=&password=</h3>";

	}
}else{
	print "Content-Type: text/html\n\n";
	print "<h3>?username=&password=</h3>";
}
