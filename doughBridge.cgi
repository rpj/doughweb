#!/usr/bin/perl -w

use lib qw(/home/sulciphur/lib/perl5/lib/x86_64-linux-gnu-thread-multi /home/sulciphur/lib/perl5/lib);

use Dough::CGI;
use Dough::Log;
use Dough::Config;

my $log = Dough::Log->instance();
my $cgi = Dough::CGI->new();

if ($cgi->processQuery()) {
    $cgi->sendResponse();
    $log->log("Success.");
}
else {
    $log->log("No response object.");
    print "Content-type: text/plain\n\nError.";
}

$log->sep;
