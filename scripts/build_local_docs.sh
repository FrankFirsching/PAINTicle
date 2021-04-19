#!/bin/bash

script_dir=`dirname $0`
docs_dir=$script_dir/../docs

cd $docs_dir/
bundle install --path vendor/bundle
bundle exec jekyll serve
