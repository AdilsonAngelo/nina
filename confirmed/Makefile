clear:
	@rm -f confirmed_cases.zip
	@echo "Done!!"

clean: clear

zip:
	@zip confirmed_cases.zip lambda_function.py config.yaml
	@echo "Done!!"

upload:
	@aws s3 cp confirmed_cases.zip s3://nina-files/lambda/confirmed_cases.zip
	@echo "Done!!"

update: zip upload
	@aws lambda update-function-code --function-name confirmed_cases --s3-bucket nina-files --s3-key lambda/confirmed_cases.zip
	@echo "Done!!"
