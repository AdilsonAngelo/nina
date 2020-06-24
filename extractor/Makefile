clear:
	@rm -f extractor.zip
	@echo "Done!!"

clean: clear

zip:
	@zip extractor.zip lambda_function.py config.yaml
	@echo "Done!!"

upload:
	@aws s3 cp extractor.zip s3://nina-files/lambda/extractor.zip
	@echo "Done!!"

update: zip upload
	@aws lambda update-function-code --function-name extractor --s3-bucket nina-files --s3-key lambda/extractor.zip
	@echo "Done!!"
