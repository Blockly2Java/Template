#!/usr/bin/perl
use strict;
use warnings;

sub decode_html {
  my ($s) = @_;
  $s =~ s/&#(\d+);/chr($1)/ge;
  $s =~ s/&lt;/chr(60)/ge;
  $s =~ s/&gt;/chr(62)/ge;
  $s =~ s/&amp;/chr(38)/ge;
  $s =~ s/&quot;/chr(34)/ge;
  $s =~ s/&#39;/chr(39)/ge;
  return $s;
}

my $data = do { local $/; <STDIN> };
my $pass_count = 0;
my $fail_count = 0;
my $skip_count = 0;

while ($data =~ /<testcase([^>]*?)>(.*?)<\/testcase>|<testcase([^>]*?)\/>/g) {
  my $attrs = defined($1) ? $1 : $3;
  my $content = defined($2) ? $2 : "";

  if ($attrs =~ /(?:^|\s)name="([^"]*)"/) {
    my $name = $1;
    my $classname = "";
    if ($attrs =~ /classname="([^"]*)"/) {
      $classname = $1;
    }
    my $type_attr = "";
    if ($attrs =~ /type="([^"]*)"/) {
      $type_attr = $1;
    }

    if ($content =~ /<failure/) {
      $fail_count++;
      my $message = $content;
      $message =~ s/<failure[^>]*>//g;
      $message =~ s/<\/failure>//g;
      $message = decode_html($message);
      $message =~ s/^\s+|\s+$//g;
      # Replace newlines with <br> for GitHub markdown rendering
      $message =~ s/\n/<br><br>/g;
      # Collapse multiple spaces to single space
      $message =~ s/\s+/ /g;
      if (length($message) > 500) {
        $message = substr($message, 0, 497) . "...";
      }
      # take $message and duplicate all linebreaks:
      $message =~ s/\n/\n\n/g;
      print "❌ $classname.$name\n";
      print "   Message: $message<br><br>\n" if $message;
      print "   Type: $type_attr<br><br>\n" if $type_attr;
      print "\n";
    } elsif ($content =~ /<skipped/) {
      $skip_count++;
      my $message = $content;
      $message =~ s/<skipped[^>]*>//g;
      $message =~ s/<\/skipped>//g;
      $message = decode_html($message);
      $message =~ s/^\s+|\s+$//g;
      $message =~ s/\n/<br><br>/g;
      $message =~ s/\s+/ /g;
      if (length($message) > 500) {
        $message = substr($message, 0, 497) . "...";
      }
      print "⏭️ $classname.$name\n";
      print "   Message: $message<br><br>\n" if $message;
      print "\n";
    } else {
      $pass_count++;
      print "✅ $classname.$name\n";
    }
  }
}

print "\n";
print "Summary: $pass_count passed, $fail_count failed, $skip_count skipped\n";
