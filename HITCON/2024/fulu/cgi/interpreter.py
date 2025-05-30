#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
import sys
import hashlib
import glob
from copy import copy, deepcopy
import base64
import json
import os
import hmac
import hashlib
from db import connect
import random
import re
import time
import aggdraw
from urllib.parse import urlparse, parse_qs

fulus = {}

def buildin_globals():
    global fulus
    return copy(fulus)

def buildin_exec(target):
    return fulus[target].Run()

buildin_func = {'open': open, 'len': len, 'dict': dict, 'range': range, 'exit': exit, 'urlparse': urlparse, 'parse_qs': parse_qs, 'int': int, 'globals': buildin_globals, 'str':str, 'exec':buildin_exec, 'connect':connect}

blank = '0f95db548dabac35f579cdc5f0666b7c126c05ad7382e12eea09ee29b22caf6242c9755fae3af452eea078b083475d80d8405bafc75cfbe46e7ad580799b94d9'
symbol_table = {'336a10e63ff13be4c7d8dd0a99e691a68dcb06a6e3b6c72a53dd5f9a383c1c9f8a72dea4a29335df64b909b5fa06fca4a155013b408e14181547001a12df7694': '0', '705a0a410e69bce3990a9b38767cd133ea3a2ec379c2c358e40ee88601efcf91d2481c373560ce27587342c674cda87c554de2182264d86fa8d1cfb49043786b': '1', '3aba5ad621467d1bd30c3c121ab8f1ed3ecbeb4a9522fb9e222800a3ac70432c616017aaa5b37a35608e6689e4bfa7f13b4ec1743e4d0e6ce03047822c40645c': '2', '5197464c8233c497e82eed18a6da748d58e98cdbc608894230f399d3b5ab486586bc4916c8dab409a5e25b98026cefc07dd133edea28199e841d4c6e9b7bd45e': '3', '7ee91a54f1f87f8411820a78c174da6d8c631f0f782680d24bcedba3638ccb3110e4d0520f905bc9aa14a1b7df1fe8770a1100b26f083dc3165250529b457d5b': '4', '9c1d370a236a1222172340574e6ec5192b108405fa9183dce20d2c0f58969e1cb8aebe19a1e41beb59a9ff6c53966fbb5f4e2c0005f914288866569a59df1d7b': '5', 'f7014c523971ca8e113f373e7c0e8fe69959664328d174977f74089eafd31eecf09da0f4a4dcdbc827f6d9bbfc76b1d33835e7cdf562af90587252fe36cb8b6c': '6', '8a4047e88ce54c9e65b0c390f738802a4048d4dc6baa0873f89ec108da6e52fadb05a9310949453c620fced7349f8a94e8c3aadba99b149760a4f45259ee2af6': '7', 'b7a244840f391a34dff7527fb1b7422d33480f68def7c5120bd111c2f4254e72b8d85357cb28e61801b4d91ffab176ebf863b98f95cab3238658ce0d756ed614': '8', '61b27ff792f139831e62756495fe0392b62f5106231a38a4c04a0018cdca58ffa2aa315babafa2d46d9bf4ebb68c8e13b23a1868210ca60d2668e32b94b324ca': '9', '2dc11415528dd3f12b53aa59cc81d70417b34a8f31aa4f540d0f2f312032634f490f7b25f2ff9359df7a34807ddce5f5aae8fe9d827f96aeae966208de2ea6c2': 'a', '2fbf2ef9d3aaa544f2985d83c09cd06b9ba4ccfb16a0458f61712d777892a331ace9238e77c0f9979282a593262b3c3456a4446bfa5a9b625c5b1028a1d28f80': 'b', '1d43d3dc78ebe22645e6ea90f06c145e78db407eb7000a4223abe201bce222121eaffce666a27d6ca34f3b839a64854973dcdf88a9a170b32a750826d45a47b7': 'c', '1024839f32d1f8fa66b25f8f4eb09fefa645a51c1fa2429671b5d717f5c0b59577a160ba12692fb8c3b235ed030d4305753f24c4cbd7f637d2dbd8c7c6bf27f4': 'd', '783cf065d7728d9e17805e98defe9bf355f5302e2ac7f41afed96706cae761fdb6b57ed4755561633bb472d1fd696a60bcc45b729b0a3ca6ddf5627204dc3933': 'e', 'c6035c08bf112ffbdb8f45014c3423e6769c4717b70767c56373eef931eea5110fa3ebb79116256ecf4c85e2b1488cada9bccba9d150e5f896160802679e5a2c': 'f', '28f7f148ba49524f01a3de266a0eba6682beb7ae227d3a9cd4d17f29f5103c227634cdfc6c2e32e676a5e6f5dadccdbab892b88042da701786072482991c16f6': 'g', '8da1418c1a95ca4a23b910670c9ba085141bbba2fb15cfb40260fb2698e460516306ef73cedbff001fd469ea2fb162f402e36aadd50ab998a1d18209880d44bb': 'h', 'e5a4788bb10c53f74d29b2d98b0591ca08276cb3a2b22518ee4aa2b55cacd5db55aae6dacff4c8e0434e78e13631a073db4916b7bd5910c82b08153a180a7d21': 'i', '80c642ac1e21e35c3e79485b4a4c4867c5721225176313ad45553a494561bb5cc6a537b775a233538ee84ca3f5eb1203053abad0e0cf993c9272f4b0d5f4906b': 'j', '3a5a116390e640613d54f49ea86b513292868af07f7074ae9b24479bb31277108a56c2438a5cdc1c6853bff1f7acd8f8e254c86739d0a673526704f3095bdf4b': 'k', '04780aed9a4ded6e72ef9091bb80c9f2e01ebf91a04d69e63f602f010b0a5190830ad19fbf8f775d7fdab0184a159d8fd24b458b0377a2013d79a38555207dc9': 'l', '19c5b2ea1bb401f0b39f16b1092a89ebf9475fdb6dfb8dcfefac1397c3b39d69483aaf35583fb2e2ece4f1b92920c70809f8597474bddd2c7300b8f7db672052': 'm', '5d03d93f5503698ae376209adf2870ddfb0471c331d48b81804e24ca5b49ba3cff9e6367566a026a22514e3a630d3b0e777170051311f548eba6f3bafbfc38a9': 'n', 'a2355b607f757f7ff2baa6be450b63dfa9847151098bc7808b5dfbfd39adf7d0ed583a05adc26d7fe75adcda321484f76888ca5fe162a0bc2eaecd9afdf646e7': 'o', 'c33e592f17d1b77187675b153449a918ba5890e20ab7f2bb7c7c7c452289e951aeffb2029f167a4298513b3b27ad45ae8b14feb3d973745c76764b809351f1ca': 'p', '3f3e4ec03221999218a4fff162db24f28fb1e13038a4af0f44b1df5f9d987a560987831f36cd45a02779c69e3037872b06e06659947de5b0bea22f5859424909': 'q', 'cd471a38c11dcd3e16152bfb0f1adb8b885a83cc5341a4471cce8f88634e1296d46e05b789cf3872578f064bb2d1f51e9c320e0774e70dd8f0585386b005c6c4': 'r', 'de908502cc5d15bd96279b9d25f3e88cad71bc73a29ce4897c09c92c8095c2a9f229abb02c7ffe08d42a1a2adb6882e56d094ed1f11f8fc5d7ef1b169c55dd7f': 's', 'e569726e89e8637952f056dc9722101f0d7065d4371ca58d455870495b0cb706e6a3e99d1ae51399d328c188d332263313514dcf6b3de1fdee41cdf148d4e2d0': 't', 'f85881b2dacb4627a365bc73a0647c5ca4bf38eaea7c07f08c4ecf5211998984e0f4a45d3cb77f0a67803597a8b640511ce171d9c9272fcc50309e762b28210f': 'u', '587aab2a06fd12b74f6645a16b58d7a3ab9b94ae0795448c3f99bd8f4477e669de98cb48a9cac8078d30cc5ce703cc9887d67ab96f6989b596a87dcd23e158bf': 'v', '643adfd23d98e47cbdea03e38931f0bff8ab32079fd9d24f0e0b82d25ea2166d6f546f960efbb220c9cfb8aad5ced6d93c2d2b573e36b997cd24e58f6302ea06': 'w', 'f77240708a929334399f3cf558726675dc058364d7c3936e5a2d36f1549fd41eab1c3a41733e2915d540ae87443282f25380b92079b9749cdacc6d79cf644f12': 'x', '58791b1e5f37fbd3e06382917783e1122eeee1072f230b63c6b73ccdd37e1359edfb2c63558426cc3c60ba09595c6b075cc61592fd858017fb33609b8bdfcc9a': 'y', 'e6ad62a570ba8c76e65bd21e866ad0d539ecd12572bca195a5330c37c2621c7494b713d8b90c03575131c341443271caa5bf754218fd4ff16cb07ae72b5a4ec0': 'z', '7309956bceac8320e644c95741e26becbcf9834e401f7e20b36bb907f9ee2a0e7b963ef8a89ccf7079c84b6b0dbb3d700fdb7ad8eb8bc4d36ba3004de9476f82': 'A', 'b455ec79d40e00edc679ccd7a690756894f9b5fee2439681afe70179c6b69a07f6a5ed47dcd77ac8fa02e6b63e4c4b329543487b01b1db32f1e1a99540e67f02': 'B', 'dd7b680463681141930a778ecfa9a5c23c9ee1798c96170e6499ef3ec74c352339f6500d13d3c1af670afb05c88040fc3f354b8d8f352a570108e346fbb11a00': 'C', '4554d93e5f3fb36b248729f229b2d24b9099116ef5b5e5cbc87865f2993526d08865e9320fcbbf74e79f533a05679718bf4a147008983bc8044c651f61e975c6': 'D', '8e87678fcdcfa6da641e17b853a3a59848d20e59f08400e0d7a4f4c317c29e35d2ad23496ca5f29cbcc6221a651cd11f57ac2a7f103844b9d4d373e591cd0f08': 'E', 'de347e659faff2d4dfc45b4d8d839ae3e28e22180342e2fbff9a83ba3f7083a4c303134868339af78d97cb8126ce182ae007b7d955bbeff91728008bc510a638': 'F', 'a7742086f5a3618a36ad9f7585b10aa38c122f5331aee96888a40a25dd169ddcd5fee474d783aa29fb446d3f42889386ad4653b6d662b1b5d7c8c2403fa23f23': 'G', 'f86b9a78ab81c634203cc30536a62a7e75f2537279ddb136996a2fd4fa4039be2274c524ae81e5b1d5f7bcfe38b39e3f773e2843814b67baff0a636d2546956e': 'H', 'f4c9d56c38c8ca875363f6f48d0471e77723cce51c9c83b23f433901c680a9a521ac7d9025e4a7e2da4892f90221865331e00cd8957e0ba1c746b46d4afd5228': 'I', '129b282524ebab0c206b568991cea41c73ba1c41958cbf533918ee7aaef930f19b9df3d6a0fb9be370386e77c23ad6d8dd2371113f17ef70224437eda1d0c224': 'J', 'f6aef9cd0ad894c98f901c24c0c8252dc02204c1b7bee93abe41740a6fd38527e5136db95abecb5085236a05667f76ac608385535314eadeb4b6e676c4f5480f': 'K', '7f155b7d94b1d2642f5616142666c896c1c1022c16f24670b5de62dcc082f4f4af68e3750cf75f0e6720bede1c04edddb1ec455ad8d78190b847501950335a0e': 'L', 'b82185cd36d390fe6e7f29c66a3813b05366a879160d45cbf1f54bbd12263f114c24a7b467aaa87ed46461e281a60de62c705ff754b99afc5d5f575045bab4e0': 'M', '622f46365db8b4494457e3c33e7e551660c89912f4c5496402d67b98ab435e33434678277338366b131ccfdb8cc82d70dec50db93cf66b9c009ecb71ff63e9db': 'N', 'cae48dbf29275fb904bcb5f6d91b7e8642cd709935f011b4052c4ebb89b7bdda70baf58659693f136ba28bf324577d2751d2e264f304b84bdbeda889e63385e0': 'O', 'f6be502fe6698f8fa8b7d680fa52d8bad1bdd82da53ed51a24fda126fd1921f518b67850b2f723e562c4a86bd2e7dcb343e12e53995da1ace2c18f485e3fad4c': 'P', '144f514db9a8d8a539847588adca9504ccae23bd9512e3609eea7d60608430a6bac239d75cf27ef82edb1a6cd68887f5ddee0445ea31e19fa6034f0c40682ede': 'Q', 'a5c37c9eaa0b6e47a86bb976c1372b516ee79f93a12779124a99554e37abdc9d43fc6926600c4461384640c86b498c2217fc18fa7d5ff895935716f01afa17b1': 'R', '6960c050a6ea1e0352ef99075c8191e576c6b61bad50623c30147f53c6f4578378998caafbd1b216b5a912ac63729a23eae1358b518dd8f863583a281ce9895d': 'S', '08a40bc26ce5273d74a73c59c6af33feb6e69d19ca024494524b67bd6f5d156faf733a748bf4d686c70111d25df3ddccbb3ef015ceaf976b88fafd2759d23817': 'T', 'a1859a25275ba3115f1796cfe44c7d591b72628b5a88dae9cceb11f651ea0e67172b264729bce9346dcfb2c5df17463ddcde54decd5c5f0514a98cba38001314': 'U', '4125a926a7aa85fae7efeee23ec2af3cfc2773f1cee8008d0656f9a85de48e05b9ad33bf6f8c90c6745ee06de15991a325e274feca21b33e54a53b59f1b15e54': 'V', 'd07cdcc080f2426b7d0ddf2be6a253fc3da79970d5c322b543c70564e708d142936258794edba720ba92551d1e3e9d8ac1c12515ac880c79772221b9b9536a26': 'W', 'c6af7c9340829fb371f47bb9ecda300a87ae3a7c2fc8c98e7a09ef662fc3e561f7ca91d7572a6b2e32c9b628be6bb87b59cab18890a407c53fa06553dd798cf1': 'X', '86331ab823d0e7520d5f83c3e2e8ccdacef909b92971b7c761cf57656675744ea0a456ed8b3b572f0921b5a76036700d9437517a8700b7c6d77322cb10c2e710': 'Y', 'cfdde85fcded4673a42eeab91e5f6852167e828fbf892ac124f4b50b782c1fbb5b55ed11db702c66b7c415b5558548a70a636063648b7c922f88d493c149d1a1': 'Z', 'a72d12f4ff04b83c94ab05313dab81ec2ddea80f471e1d10b001a4922eca806940502b5934c0d175a2dbce92649141bc6cafb2a3a971740af3aaaad1b7ba8c32': '!', '5a04f8c5533288da1bb11c2726f2b23f1dcb39396d2defa28febb8e8c1d780aa4db690a351a5d3ced8955ea5964ac36469bf66d8ea76791c194bb726abcdd809': '"', '43f038c56674374b3bb265c7adf5171b87d484432d31a5c92b4d2cdcc43adf548a37e50e5a1169c9dd2fa49dd5efd3ffd456f05865a1a3c2799207e858b5135d': '#', '88fa586ecc123384f20d32881fead601d75e6c6dae182c8eb98eb19216d84961cca13e138cabe12ee6a448b274077bbf89dc39a9e597aa99344d312f8f59d466': '$', '3ac4d39172763faf9d4c2330d483cf5359a4664fd795ef4c1ab54c077f2d429e7465f4e05ced47154c23e944870b32a300437bf58b47cb9dfe5c20b88d0a6f9d': '%', '846264957761b2edcfe570a6f3cf7cbae3965fcc5c942f9cce1a8b2e9e77e9ebff3a7b2d3e1e8a09825bc36db9fd77ce19e5a7acd216d3dd223a675b7149a62e': '&', '1ad3f9b5b9c161e53482878f7a18abcbb5ef473e301ea1428ec2684400a386be7f035e8832242f4a69fe6ca3e7e45cdc83c1ef52804ecf8c51f020e3aa743dc9': "'", '2d6a710336ee7f914ddb7ee54d55a550ec1eedf4ae2f3bb6cc534993c7ec311fc362965089d5dd6f10e38b4ea9942681bbd6fd7ff43719959d2fa40a32809878': '(', '6c87cb639341f91cf55f2981595e93e24f913d62304d8da2eaf188fca061a0339d446acdefe272204b3f79850b2e3ea8f62bf8d958eacd2d6193865c46d3fe66': ')', 'aec7dc3e752df62a4cfa4a817725f8dccb7d0a80b1d926bf1361e4f0074770c4e002067bf6dba15f233314d107f3dc4c200ba30c7e6d79c73f66e20b7da02cf6': '*', 'b35a3519921a0305f1e6fcec11cc43250136ffcc9c5b19ffc2edfe9799f6a7a027b8307293572651e50095a0e1163a86898e8720c8db1c80c13940fba51a9c69': '+', '9a9fd817a0f803a274b7b1ee32daeaeb5d48245058fce7ad1a94c3369959ccf3b995c54755cc50bf52cde1c5d633ae31c817e09cb63d61c344582529e8264096': ',', '586ea60275f9b1da5717226414d9ca48387c7aadaa55ec3be5db0c710bae7ca6bfd22164ee08935322542d0912cad734305a76a7a7cd4af3d4dc1cd7b2d5cdda': '-', '2a5f5e7653e142e33ec568e0ebdc5aae9fe0908809198487b226b8c09b4695641ada7ce5f0b7ca1611f0513c72f34aba70042810143ec92a3e4fa119974d73cf': '.', '44c4a3df374b595d761d597fcbc7d81e6789d0013df4261c06d133563b49f4a889c8dfb908234758f6e29c69de6dbadae7bda3a5cd8b42623f4f1292234a0b2a': '/', '13756137d686a4afffdb6bf4c190a6a5d245ed5e5af9fdd292e2fe9f8f4942fa80b9964f162c3095621eae0315315513ca4a6ab2612c5b9ba0eca9cd3604cb92': ':', '21997d118b3007a0fafe9f94560aac8635c1e222d0c56b8caeef61b2e55070225cc0fcfb126167d04c0f8ab6f91a43bbb20e74b1332e4a568043ec70ff5b73d5': ';', '69841cf857dbee0efe1a1e203bfbf330f1ff8e25d454020d9e91e1a1477fed11698e13d2b0310a277a1306d10be3fc9675dbd424a19e0bb2bedfe16dc0360d81': '<', 'a3ca9ac4bfa16e16b30dd40c4b6cff6adb9a09ab373550bc5c8a1d21db8d23373f3ca12e587bbae9aeea4110f1eac86d45f7f4695791217577a891738aaf75ab': '=', '806658c28ca549bcc2c0e4aa190234fc324f9d96b2b6d61cb57d83b596780f564a92e7dce4138249f68537d09a7c38140803d41cc99aaa7d9a5219beb2798575': '>', '390d07a0ce55f12e8298cfe9111f12a902617737b5fe3dde445dceeecc4830a91e1319cb5a8fabb41d8104201e7c8c56b0921fd76d0a1b37bf270b11aaac017a': '?', 'da55d187f6dd1b76b5f9bae82f2db041143bc7be5b4760eb959672ec2cb391538bc91335f2004aa951cf434deeb8faaf2f22a8c0c40fa03f34519ce75b579236': '@', '13560c20c0636568c945ec6219284fefb55f2567199b46286539c3fee20583ba55c28e39c03da0f61e166ebcb4b9f17a1d20e22fc3a2f1e83013fb51f850b50d': '[', '925135660bfb6582c65c9bd256bed342241431806f3f4bdc5c0ff36f99b80b6e63b1e657faa1d2a5ae2865be9c6fd14a5a27c3821e99af2e08268c5b4136c763': '\\', '7d83c5a2985dfd2ee625104f219e8e6c8b0713f54adbf7890d94154e93efc4e571a2708098ca2d865d9b7e91bd9e373556acf869020c588cf5d821d32f23065c': ']', '50cd71ef15a12e179810ad599597bf41203b86a5840256f1bf8148b327f2945c7f6e3e9bc6341889c29ef76a474b6302358aa90b9d0c7233b889bfbbd420f04a': '^', '6771c87a99ece0bce9678be1aae07e051aaf6b85db70f6792e55e241bcb6d74eb4bb9dfcad86b05913d4e33b5fc58647a3a6346e1a515fb8d21cafcd593dca0f': '_', 'd571b566b7aa43eee35ab39d43c100c912c97cb8edd83cb321a5c94f9c8621455854063e8e9f99b59b6da74ed2efa5006720590bcc9cf3cee35ab9f7c4ce7031': '`', '92117c3f6f97ba22e1df8d7ff00877bf57c409852806eecd72aaad2bcdb9899c93703b2a17af400ad318e1ce3f65f725cac5e49a0d54f9464f99b3952997ce25': '{', 'e4dc90ae5479ccaf89feff69166a38a040111026fdb1b19e4b89b8082fec1730014dd329a917b6ce78c73dd5c73e460c1620afd5f98f0ee8cf542c30a751ba4d': '|', '80b10978c88bc1b78ef50e4f6f28c1b8d9bfc26d3b09f43d692068ec92743deb87254102eb802cea504f1ab534b5f613343933fd76abb024f11ee46fb313275d': '}', 'd1fb05b285833426017b945d19ff9ce2c23702e09ee1bb488d3eb13bd202aa6f54bbbcad7b21a6b54d6e1160fa790038278c04eaa0a094f9124fc40e1549936c': '~', '4a85a7db6cd0472f63703f85bf53814fdfd7a7018da43f283234d0ee6fa0c4bc549864aeffd891ba06753410904bfcdc538a53a5c051a637cb0b06ce64021fb8': ' ', '62ccd9c63c1ef848730aa40aeac5fe8b8225dd9394a55f36ee78934c26517268819f2a2772b27ccbcf691d51839a48c4412387cb0cc235cd3d35c3c9c016438d': '\r', 'f92b69db62580aef95b4380078a85c07f064186f9d1cd784f07eaee588c062298f43efc4d771239aa31fcd0127c0199620b6ac0407a9f7a6c2904865602b3e4e': '\n', 'c3b2ca45a09a1759629adf9d72da10cb8bab0b872b15987ba6a16f8c6c2e11579d75cf196baa686d386e61df02abdccc0d02e627113f91171972bd12ab128b6f': '己', 'ba9572f9517cd6ab8db2a3435edddc2910faf853b0046129e76811ca672e5f1ce2f61093af2dc5b51d3a876dadffaf7a4f21d0f48edc9d89ef15607591b9e508': '癸', '21aa6bd41e5090a2a7f27e2db73a14289c18ea65f3819da433e0f776eee4a6e8888242021556654d0a7128c2d7657164cd2883f0cec69e32afb7982f5319f0af': '庚', 'b43456fc55383a95ea8224c5a58a92d39c65bcd179a6d877f9f48d68ffb975c5c3291001db4f672715d6c59fe297c8d3ab64ac4239ff1c6011ea74afc63c6ba7': '戊', 'bb93908ec667e1cb9a1b5c4592c046bf6ebbb49d1349ba51a7c952f5e08528bff37536e6587025d23669e8cf6b0909cc9130a485926a76f4fbdd39efeb1303b1': '未', '22fcdc0e1ae8e5af1ea91c1f0c977a04ac90e91042d42431c444037b1ebd8e87451ef9afe8c0070150e221b0d42ce1d2fd554a60ff635c672ba6e79011851fc4': '寅', 'd9e6c9b957e28708d03e4b33b61d7e08ceb89563203da522b4e4ed3ad2fdfd8ee0988cd790f28df92c91988a4a852fe9b97d25cdc733f3f5bcbf6cd42616221c': '申', '8d7681fc9165b209ed7b8ebd76670631a45735a5ca87f587c50b81fdb48f3403c0d81e1d4755fdb05079d1409ef2a11b60505b1dae98a88243d9749f765818ef': '巳', '5340070ba5b306ec3d8381e089a69d08c9d0807d04edec524bfaf2689ffb38a1e06c4a0e3557e52906247befbf54129ea3bd5ff2f8079e518e0f2472f8802c4f': '符', 'f4c50e8512fd8e722e747c99bd9ea183021f3c69542a11c677d35aae5b56f1a5185c66afd8313bfac4c33d7de056ac3477f09e7e46ccf926bc437a54d38804a9': '咒', 'c177d30a6f223f1ea58480fce95405dd37876fc8749cf50bb60263712f34c8a30c1713c4ff34f327767564e98b94555e9adf1f521f5e7e2df4a73ad672776eaa': '甲', '4632e0e4828630ecd5a0c4e348f8f28744bc8f1060247729db0fee50fe035ce3e898b6690e31d6fffe319f5a6cb67a74083e27acd587b9676674b1b8f6d511dd': '丑', '337f44c90c048e380f0779595003e3c44a70023f081067802bc8fa04b3453fcf58f6e0eff433dcc6caa454123c91d43d243e52eb25bbdac41984340edec19e34': '子', '236ed2c3f0e108b6035e3be5808285a23cc2610dbc2d9a05b9e050dfe5ee9538737fc8c0bffcf20a6e96360f028abc452d7ebf833701d1404b5285c4bde406cb': '辛', 'cdc7b2be140ded23033f92b038ff8c8af1f5cc4a1844824e3cfe47f8b53b85da49096779d38cb99fe0164642dc89970ebd9e12314617d065a48bcdc624683ecb': '丁', '0d768c9b8143285809bea80cedffd2a9d5fd909e24177ef3f11b93f2c1d3f782157cf136da26c1e0acff1a2aecab01f91cced4abe60bae8c9baf0f416f65526d': '丙', 'f1462737f0be10c1d2d46c62e5f0122b96994a5a6f3db83fe4a1181bdf1d02e2e0f27264f6d3e4f4cb5423645a5ddd1550a64c0dc82793507a65c8700ffc9448': '辰', 'fba33d8235ae2b1be8bdea8ce73ec01f7644f500bfea755bed3d18e2df4072c0d9e66137c8fd94fdfa16fad4e7480e7232b8c7deeb565f910fa8865db392aa8b': '卯', '0127c456e2957199c4613d0ade2d5394896694ee642a1ae7ebdf623797ca10ce556baadda1e1167cc3b4d3953c5e9147f68532695ccffe4ef4bf7a49d668a441': '乙', '46c88929c980d54f320d6397760fa46b7e5e51d90327844010ff7c4b095aff5312cf6900f824315cbaeeafd43f861466da8871f778f02894b3ac62cebafdb9a9': '午', '577662c6786e9a8c0ca9c76b20e4357491e7818168e9958c50a3027abc7dbd56e12565b371a17882d599b689a31426f57c6331d8910699a2ae2f9b37f9d05668': '酉', '97ab0d96435deebc8be2c489c29010ddd6adfece7beb8f750c660f151574443202d060c4b97bbbab1a4218847bd73237450aac63685ac40b91742977ac863599': '亥', '083d40bce6a10fcb5c7f59e49d88cea05b89e1626a624d3f35b254c08941f75f0b0ad8c65d2587834fb16f11220296d9d3e04b82e5813acb954076899c53fb0b': '壬', '3b38db6024911d87666c25a00538f48ee0516a2367872e081216fefa9142840fb83e0cb1f7726c7db9bf2901ce7ff56e3a3fe425e6e16f633ccd0fd84fcc396c': '戌', '6d60ded6968feda70c85230e53a8d0c9c6139197ba159bebffb69fbdfc7767aa31c123178c14507c777cdfa66a12d30c903c0f32ab891badb948d1abf7aa499b': '炅', 'a398324d3f7fb275029024313c3fb98254847cfc71e6d5375cf9eedd6a555da1ddbfdfe44c48154b158583c95eba1bc799da625444c79305f6cff5dadae20762': '令', 'ce0758901d6b6f494345b0439c08e3799b64235017215bbcdf567aef5c61caec3823e73f262733ae2f7c621a2ca5d052cf9c00bc845182bb354f829faf5fae0c': '若', '9b2d7d0894a41e7f4753eb89774932fec5308c4bcf461c60601c7671f5583d1a0b7b8f3900e753a17240d4fcd1e0d07bae155c002cfd201c495885479c0a4c43': '喱', 'e053860a6b7c613f88032ad3bc03b0e2d5ee0c96853482ba0f0970b82496d0c00ba066cbbaefff0314a2e94f5ccb8e2d2f6d0f6a93737c072ff7c74b0eb5d8e8': '拑', '9a7e8c769c76e952a45d6955180dd2755fcf784a85ac02bbcfbd572f3f350631d7c5d48e16734577d1b21fa925a8ea3ce864e96165da19c4fcbeec19a2ba2a16': '韔', 'c00935a342fee8e108dadd7fde64342095d1fa0e6b03d3c67de987a7744e61cedff970c215f989bee4adce1e70f66c05812fe49414c28d7b6892bb5165899049': '趹', '4fc874edf4188a67d10e8d1423836e2f641c608425a29fa5c6f426425ebad208ac7c1adf7a2fd90a052b58c368ae43e752af04385f0113ec70301c0809bea85f': '夢', 'e49577721d85341e7d2ba1dce9ab4018cfe02918cbfc3f4d92513c7e43affb03c2903bfdc27dee68b8a38f7cdef3847bff3efa38fd2d8877aa50aca1fd9d41c9': '椁', '0130e864fd3efbe05709de51da008d5f89cd9eae8b2aa11c7d66992ecbdde93af18da1a7d318060de351ff4ec021c0f163e84a28b58b78a4a663713c6f4aaef4': '瓅', '0bf27720bad3934f853b2b172fb206afda2e6c99aa444dd995f82e0b3e0b30013e49144b4a19f2f3afbe67ad0b6cf94c0a7ee0e6321e9a91e6b9fbdd2819575b': '瀳', '7ba7c4c4621489e7a2e52220a801369fe8685677d7f9a6aef76116029e1f592426b895e774cdd34bca445216219895d1d84735462365a777252af19b85b71ced': '適', '472d98c1abf845b52ba6eb4540fa7d4dbb519a9041620c91917e1e478c81979ae8398704eb54a2472568adfab92751c77d9abc23643eb02e4457281199ccd4bf': '鏡', '96de60833d3f7b8bffd83dc3632dbcd0eeae9c4a33d184db87c6152cd4b82dbf4b2f312b3417be63bd4fa7a8c1fedd1c216e06ace5d8c33ca5975480361243b5': '電', '4aed7af8aa59a76d26937c9843d450664bd7c596d9c0e2a759d9c160c518fbcf2725a1189f861e79d92742929e737567b4624d35e89b300c984c883de5f971c6': '怏', '5cf2dbbc63dedc52b72b2784445ae33a81068bd9fe678d635e48678774be9aa13c22d6e5d36978a45376d5a0327570fa08009a9694868e2b61fb6b331a9d9fba': '槓', '5c1cd8f2fadd9d96f76ec1ee35b58f6390aa9fe7ddc91be7fcf835d6c42dd3a21d2f73650004cedf5e2e2f8fea25f2c26702b042b35e81f27b6dfd8d475c56c4': '肖', '9ae13e077b349817ca5dfedc5cf7354ef3dc47e391b3a6cd01a900e49a52d609d94326d997b69a434ba899a3e0072ba015c99f55e8720bb8b909b9113e5f1ac0': '余', '6414f50c932e7885ce4323f24551f0d48a5176965d2b41950637e85fe14ccc7c178320014c08f17184052026f9a55574c3ff25c35a9a9e3c6d974e6c47df21e4': '槐', 'fd1e35ceb8a44bbeabe5e637ed0913063691435b2bf4921313fa7f875aa64fdd8811fb5510bf31558fc270bc103f4c92949054f339cc1d2561116e918b673c63': '飧', '806a0cbcb45b81ce8c08f46d11755b724440562e8aefd858ac269b7bebd2d0a52647e9ea9e3652b1b8144592857dc552ca07224995e139775901ffab247bf706': '嗔', 'e177f788c9d60631a3ff506f9304a7e4b51467de3a639d89c759040d56a0ed64929248b034afe0f89f24337ffb89fa3a2f0ea9ae52a7cdd63fa6d627b9918c21': '𪊨', '6d02f5a457441bc4ad02ebb72cf3ae3f839a12dbc6d3253c41cb57f0c49c9b621ed9d1ecd279b8eed49d618d748ff21ee88d794ac451c150bf5acefaca6f577d': '𧢼', 'e6a9b80e6350893770922f618adbfa9f6821baf5ac0decf6426c4fd3917d422997e683efba857a2ac9008bd1b3d1ecaeeb63fa8924e48f49074225f1fa31acc1': '讇', 'f214b711829ba25b20eca705514988b4b26c26b683a1227ad4ba8754ee69eab04c8f857f3c8c61452ec1851f70c79de36296375e8e881a3e9a43f9ccb12af721': '𡚮', 'f284dc0b1e3668353bdd0ff6a1d626fdf6c7577bbb840cd64bb266a55c09f1ccc8f0969cb506a783a65d2c0751aa8183b32610ad0634770aeda5437a86703fcb': '䊆', '67382fc16a49f113089de08be4ac5ebe90a1ce4f62a52a82d39c2a06e93dbea2beef85ddbdf026a777fa491906033461c3f778a1636c2e25177326a165aa2fc9': '䔃', '8bf3db85bcf9a3f7094a5fac6676df37d5e75d714bfbd3ec6b3dcc215a1e49b0ac37e9842dff5d5e4a25afbf251cbcda0c3ffb7cfb7c8d212d057456155a2c4c': '陲', '4871a0b6c2fadee9bb453d9688caba6799bf92c3f6b42e6a8a7c50959482890c5deff645f522df6b458841d4ed0a1d0e7b4a99224c6f614a5c51fccfb2035dc5': '婬', '725109888a5abf5a58470cb195bf0405c84f85d0c98768a819061093b85f1717d6987ece8110b58d077e64dc20b97a0f8e30c5f8c2ef1e2f7a07f572ac732769': '腓', 'f6358f41d734a377cb88cab90c2466fb0398215a28f5402829ddc0ac690634867df604795bbe347ae48da3a730e7d9ae870e86759602ee9c812f67f77599f168': '拋', '793dabc46a5d6c7c60b3cb07b29be6b193eca62f3820bceacbe1c63a7c1e26902c8c3963a9612cc6675219b5f9b87e461edc44ea7fa754135486e976d21f1a98': '𤞞', '02c0848b7f7f795aea94e63e50bc97d9c2f48049b8954a5b12fdf2d204b84ae6f2de75fba4d37f71f3b26310145ad1fb93252a7ca64c1ec08fd48439adeb62c2': '蛶', 'f925cfbe56080c986f6c00fc55ed61d3061f8178fc3c9d9697a63cc6e43cfcc2a799ff11b5cef2ec1d8ba86985911bb90690c67c760e972b819e06c4fc500301': '𢏗', 'b0952e9838f943b92082c79ceb05457ed929c1d344267dbf0b75ca3368d5eb27ab65dddea63e9dbf68632739eb3d3d8f362a84b155b2743cc5fb181e13a2f813': '𥄉', '28be41ca14eb443fa2599e9017f7996978a3ded654f77c5a54f27ed25a27ba954cea15b583f90ebbf25748566ae5b36a6dc4dd7b888f723989502fb48fa3ceca': '狋', 'f594a320d795ed22a633193e51e35337748445a47d0e66dd6f16a001242d517aa9b83e6317acd31f0a23b2381e436494578e7a31d4f52d4e183bdf013b650f40': '竺', '177cb6b58c169d034ea3c3f01fdc0be70295ef34c4d563148557ad27fa5012da5456b5e25230b168a3bf950091676211306d21e51f61d9baa3c62763c7381829': '川', '5d21963d91160926d6aa1fa3519946f87ded2a0048969e2652506601af6c9159077a83db6128a0731d3eb89cfbfca5fcf943d10ec2957c0d92357f7fde00fb65': '塺', '71e9182039b5a9cc2c02eda217475166564eb17635e0e105fa9de3a0139c371a656de4dcde26fb8c378920c5e518cf780f5d3f56c4fb175a8aa5228e093742b9': '丐', '877f158e2ffd288dcf2cc3f6d17554fd97876cf7f8bb896c910a7df1603d317373eff01f6fed243ea4ce54ef74c9f92a7d094f84c6594497b2f7871a15d24899': '䫶', '750f2ea545abbd8589d19bf2a902cc12740e4a07f3dde41a293acf232e62f3dca5ea438ebaee225f41aad86efa97ef5673d410d2ad4f145a9a2306b69ff66d84': '巜', '6f0bf4a1e274ddc97749e323bee799b6eaf4262e5f559b5fa1b3009f05ac15c50fc482d529533c87b71847f75a8697b9dd15eae2c3e67268e7c99d595213a7de': '嵞', '33445f35c8f3ea4b38dd1e02db69aa9f31af128d16e52d95f5723e1bdbd38a2563e94193c73d44f0380e566be1bcc9c0690fa993ad7eada4c039fb8e50e43364': '慇', 'f6ff5dd18e2fb811bb56f43fe8483c478391e7fdca23cfa38906eec4f4d4a4147efcaf6a251419a820ef7bea0aca01aed31f450e119a7c0858b0644895fe7c41': '𦝠', '88ad927255e64874b61488b86c19b592c89fe024ef525395e34d904533fb474284c11ff07d87b4d6630167095a58211c2e158c8962b6942a2eb60feeef7608f8': '騢', '3ca6b9c7177696109c772d49e871c3f019115e3d4bcae3365a04e1730e2584968a4dafd4a62d2cc4523c5d276b5fcadba28b2544be4d15ecdd4a8c7ed856064f': '𣢰', 'ab7e2c00006a92f879109d329c9f3dc8e47c5ee76a87c0035a763f0af6ba1f45795272b8b2fc2b24d375f5ef9baf136e71a958e5e31718582319aa7fa0a3621c': '𢑌', '080057af82fc11b85a191cabe8db3d45093acba0c274caaf7a70377cf6a1166ac1929fa4e6677c250e9ae0c5038b49ea137d3b873ab43eced045a45d1409c8b9': '𠬢', 'bbf9cd115b0696134773b6b4fe802fe5591ec440c8c42a2622d0f1205350858a0be622b916fa68f98f5d171ebf0524df27963ca69eebf1343c2bf1b6166ce0e3': '誋', 'cd9dc142faaf3b4163d3225268a21e8be1858413c28e36524873cbc51e81721f70822a80013a7b49228960ae49177572d002b6f4f5936499f40bea2309f3f7da': '䛄', '0e3d427c50430f48c7de94039980da5572ab881247cc1c4af7a41651d3d85c4c0f92b49ea21e20ceb66add72af67325abef459c8b50f874f690836b828d4c303': '夨', '1da5dcb224ade4c0911d34aa2b5a66755b1c0f88631b2e5831ffb3768708eee41084d805700d01aa495d13adb590d8ee1bc91afbf8364c4020b05348fd4d865b': '𩰗', '0802f89e3e9ae3af8480ad5d3d0a48dad8100fe7b71f4d71c58bedd469a7be37fcb9b3d611b0c0f98cc78fdcde4f05826c66d339bd4c1cb202d18ac89d43cc58': '𠦪', '1afda4604335bd2b3475db7a8168e1175ad7b0d396348a2e1533c427e62c7697439fb26bb5d275295fcda49564a9b69ddcdf59873d3cb3f00f5e20332cf4afc3': '尥', 'e52640a34f8ae9841368afdcaefb448ed02a7a7be6394962a56113b609e3c9a7a2bb6a118ef67b81dc2d2404f82f716b8a76c557e7ba8080588e17eac140598e': '𥄕', '68b1ea3ecb494e96d60948c3b10da5779741c5b1ea7b5837b34c28a789194ea9591326649d33cf4f16737ae8166ef1d63c326502d43e98dd50188faf353e227a': '𦵹', '914fd4b18a4eb500326681b1590c4db729901d7a11a9142590eed8bc00650fcc9898d6a1c4483d0646f2361c428e70f7667b817022dd34ad002cb7b1b609e0cb': '戠', '588d8519d2abf1d21a1141c8e33ef50ec818283409d29c21aa4b76fd544c01ab8e6f305e97b91dd32a3d676205c9b31b09406fa6c8b18cabe1fcec81ef98e302': '𢾫', '77ed715f28d8ced85abe6a773bf00a0dede627439d1dd9c95e9c41283a8c87f73478a0cbfbd31a7a7b134d6aa0dec8f49e03ac84bfce5b095ead7ca3d2bc83eb': '𨟙', 'e3e33930fc20f68265f4bd44e2c9542b707fe6f759f332eee1127baa4fb42864c3048ffd42792ee270c72d388f427451871aeca6e9a786bec1f9979ca7824e48': '幭', '8e61dc2210fd0984cb85627f21d8cd5cf5f1e0dedb0f6874f5d2f821e02c5bc79ee0ac8536f75abe4e166c6b7842b2cb566326391ee168df786bbb016cda962b': '幏', 'df2bc59e19cd65594983d9a6650500343d200772525b8576138e9d4f644ee5de26fb24795c3293dd93faa91e5cbad137098e2743f0d1d0638e9ad2b7484f2e53': '冘', '96a08435d6c699222509c210f632d627b6f8b19df741ce61237ae6b167bd194d62b389172966892462674adc9f51f2a7e093a5e2a8a9bb5b999ff96f3f1f8555': '滍', '9e388f6c59b28b366d0a85beaebc9d28ef4b8378506946f1a3ce4cb6ee75a5968e2e3c0fa07b890d20e43a971aa382dc52e6384895f6721137978d3696d3824f': '篍', '6058e6adc4c4ccc2d61a954061f63e30097de87212f5127e3440054c4eeabac22a936098d86e17ac4d2c9af0840daf5806722d0b35c369c73485ce4dd4ad487f': '笘', 'c3ad1b3a0111117154e758fc27a65fd05336e10ea21c998ba2b11ea984df4febc4fc9a6582a34403ba2a1cd17db5ee49578a9224fadb017291431867b33a00b7': '𠧞', 'cb7257e5e3b9f4367eb11112d2a77713b98b4a99bdec7db84a5feb425e6719ca8bc32d986274373b68ace2e43d2a7c7a67da339b0fc4fa9a68132198afe8dd05': '㰟', '4fa8d50ea8cb5d2124dafc569aa7f039ff1b30cb659f13f29d369777c1d4ed9ff579c17ade079af8acade3853d57c992084b9fd1951f65d7b170770a4c146c0b': '㸹', '3afcc6bee8b4dbb96d7fbdaabbd07306074c3c7e343d1cb0fda8c077a9b2cf4a575154abf736320c1870ec5673c93c3672ef71ae74ba38044330b3d5c22b5154': '漦', '92993d397bdad41fbb46c83e815d3b619e7c7602cc3cccfe1134caa3d981c33242d2b0fadb1e04d92b521dae27b14d961143afc22e7625778c40e99262cdb747': '㠭', '067f5e9201fbc0cae6cc50bf6a40ca5561cb10a1e362f9722274c7bcb30b22f2166894844789c20385540fb97512234d12a74e76a79a747499996857f34572eb': '㳷', 'f4fa069439c9113a48b274f2d7997adca8849eee7888f68efcb77f619fb2dd23a838b949b3a16087a22178411e2155b946150fde836eef06320bd44ac1b6890b': '𦅻', '69d54c169d94994207879526b0e39c164c9ff1867af04811b48a27304cbeb2b09e06b5e9500ff806e8768bf48d5a0c970ef3662d5304aa6769d9bf0b3812b4af': '盭', '6cd95936ce72b5967e9b7fb9d39055138c7dce4161ddf3bbea0f07202939043c77ff7511319b3b5f4c09ca96aceecb140d1d32f284bf19933ce46da9ff2a7aaf': '陊', '42d788832675c8c4d1d39e19e712d36fbedef7b7f2ef16821c07ce0cda4584af468eb44f30d00bd39a899151df6d66ae1ace2266f0a8dba7d905cf3a6ee4e269': '黹', 'f9da88ae7315ad0ff296a382e60c5eee53357000b97397d64d6781b2870efc0c13ea9c93fb709be25db5f78dd57eecae31c9c1e52e433fa3552bd7567f8efeee': '脼'}

w, h = 18, 18
background_color = (240, 232, 88)
background_color_l = 218

class IDX():
    def __init__(self, obj, key):
        self.obj = obj
        self.key = key

class FuluFunction():
    def __init__(self, image):
        self.image = Image.open(image).convert('L')
        self.cols = self.image.size[0]//w
        self.rows = self.image.size[1]//h
        self.args_pos = [(0,self.cols//2),(1,self.cols//2-1),(1,self.cols//2+1)]
        self.pc = 0
        self.result = None
        self.stop = False
        self.variables = {'345925867b1dd3d60ac95ca8a4416a2bc671727369f7b3659248abcb3b56d47577e061fd192519961dc95519d8df2297c1f6ec18659e5b66f961abe7f8d5b5b5':os,'26c54c9ecf40288ea9d84045aa519b4150fa3f92b33972bd755377695a4e8e70830a1910c5e8ed9ba326afa370bac3b682cc33ac68a83e16310a79684992727e':base64, '209b01af2ae33ff6ec02d2e9e5f42fd2c04e0cde253bf071df69e8bac2a61ab5fc964dad8cd138476b44986b7ae91eb3a6eb68aa0870b420aedf9432fdb6551a':json, '453ed8a3293bf8b6c494149d8b2f55cb63857847012eac58b9dacaf5bb87dd720cda7c2affb82c38ea37bc2884d6f88b8fc4d1994ab17fd0761f0b711a96dc51': time, 'd246186ff1a08372b6cdb5924fc86fe49416e66afc5645ad4d1af5d53e53caa1a166902794e79db7675e6bf896903efd1fccaf37213bb48f1cb42396ef708f31': connect,
                          '39668a1d3c12d6e7ba0753afc2080dc8384a554e40fd1fbd47665ad21a1544c54696eccba51e5a1519e5f2da42428e3220a090525d9e9de3cd512e9baf4ade83':hmac,'051a0925c598e937b50ee48f3ca202f6be5ba2cb17e08631d1fa4918f8b5338be2684447ae46674a20355e9b2396ca8a61209a4ca922b68cf9795557a515f408':hashlib,'bde0e720b6926c23d37abbb10c2720760590d1df32ff4e3a1aa6f73baa0e9b5a9bf0dee672dca5c6c7e6bac63a4541368f6b6bcdd0141491ba1a0fd468b7d3dc':sys, 'eb09e7b4569c2167dff15dcd9c6fb83a61f161b2d44618dee467ea2f58dcec08c7c6f286c7bb6b3062289c16a0011cb81280fc09af0a86b9b7f288295f04a1a2':random, '8e367ea2439ab41757d9f0e05127e8273550d5511304d339ec839c551ff66306ca233a890c7c203f9f11febf9f1682994a65eea7b787e3a166fa1dd6d792ae0d':re}
        name_hash = []
        for name_idx in range(1, self.rows):
            hh = self.shaBlock(name_idx, 3)
            if hh == 'faada0a1dcdcc0730f8520d41ff87da2337f44730a599255632394d77cddd0d955590c1edef2a14252799889970240c0ff5ee059750a05b1be6526f453cda05c':
                break
            name_hash.append(hh)
        self.name = ""
        for i in name_hash:
            try:
                self.name+=symbol_table[i]
            except:
                exit(1)
        self.args = 0
        for m,n in self.args_pos:
            if self.shaBlock(m, n) != blank:
                self.args += 1
        body_row = name_idx + 2
        b = ""
        continue_block = []
        for row in range(body_row,self.rows):
            for col in range(1,self.cols-1):                
                if self.isContinue(row, col):
                    continue_block.append(self.getTile(row, col))
                else:
                    if len(continue_block) != 0:
                        new_image = Image.new('RGB', (w*len(continue_block), h))
                        x_offset = 0
                        for im in continue_block:
                            new_image.paste(im, (x_offset, 0))
                            x_offset += im.width
                        if len(continue_block) == 3:
                           pass
                        continue_block = []
                        block_hash = hashlib.blake2b(new_image.convert('L').tobytes()).hexdigest()
                        b = self.addSymbol(b, block_hash)

                    block_hash = self.shaBlock(row, col)
                    b = self.addSymbol(b, block_hash)
                    
                        

        self.body = b
    def shaBlock(self, row, col):
        block_bytes = self.getTile(row, col).tobytes()
        block_hash = hashlib.blake2b(block_bytes).hexdigest()
        return block_hash  
    def addSymbol(self, b, bhash):
        if bhash != blank:
            if bhash in symbol_table:
                b += symbol_table[bhash]
            else:
                if bhash not in self.variables:
                    self.variables[bhash] = 0
                b += f"䊆{bhash}"
        return b
    def isContinue(self, row, col):
        block = self.getTile(row, col)
        border_coords = (
                    [(0, y) for y in range(1, h-1)] +          
                    [(h-1, y) for y in range(1, h-1)]           
                )
        for x, y in border_coords:
            l = block.getpixel((x, y))
            if  l != background_color_l: 
                return True
        return False   
    def getTile(self, row, col):
        left = col * w
        upper = row * h
        right = left + w
        lower = upper + h

        block = self.image.crop((left, upper, right, lower)).convert('L')
        return block
    def Run(self, arg1=None, arg2=None, arg3=None):
        if (arg3 != None and self.args < 3) or (arg2 != None and self.args < 2) or (arg1 != None and self.args < 1):
            exit(1)
        self.arg1, self.arg2, self.arg3 = arg1, arg2, arg3
        while self.pc < len(self.body) and not self.stop:
            result = self._visit(self.body[self.pc:])
        if self.result == None:
            return result
        else:
            return self.result
    def _visit(self, buf):
        if buf == None or len(buf) == 0:
            return (None, None)
        op = buf[0]
        if op == "若":
            end = buf.find("喱") 
            new_pc = self.pc + end + 1
            self._print(buf[1:end])
            self.pc = new_pc
        elif op == '拑':
            level = 0
            end = 0
            for i in range(1,len(buf)): 
                if buf[i] == "趹":
                    if level == 0:
                        end = i
                        break
                    else:
                        level -= 1
                if buf[i] == "拑":
                    level += 1
            return self._call(buf[1:end])
        elif op == '肖':
            self.pc += 1
            return (self.arg1, None)
        elif op == '余':
            self.pc += 1
            return (self.arg2, None)
        elif op == '槐':
            self.pc += 1
            return (self.arg3, None)
        elif op == '䊆':
            self.pc += 129
            vhash = buf[1:129]
            if vhash not in self.variables:
                self.variables[vhash] = None
            return (self.variables[vhash], vhash)
        elif op == "飧":
            level = 0
            end = 0
            for i in range(1,len(buf)): 
                if buf[i] == "婬":
                    if level == 0:
                        end = i
                        break
                    else:
                        level -= 1
                if buf[i] == "飧":
                    level += 1
            new_pc = self.pc + end + 1
            self.pc += 1
            self._if(buf[1:end])
            self.pc = new_pc
        elif op == "𧢼":
            self.pc += 1
            prev_pc = self.pc
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('盭') + 1 
            second = self._visit(buf[next_pos:])[0]
            return (first == second, None)
        elif op == "㸹":
            self.pc += 1
            prev_pc = self.pc
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('盭') + 1
            second = self._visit(buf[next_pos:])[0]
            return (first not in second, None)
        elif op == "㠭":
            self.pc += 1
            prev_pc = self.pc
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('盭') + 1
            second = self._visit(buf[next_pos:])[0]
            return (first > second, None)
        elif op == "漦":
            self.pc += 1
            prev_pc = self.pc
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('盭') + 1
            second = self._visit(buf[next_pos:])[0]
            return (first >= second, None)
        elif op == "𥄉":
            self.pc += 1
            prev_pc = self.pc
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('盭') + 1
            second = self._visit(buf[next_pos:])[0]
            return (first <= second, None)
        elif op == "𥄕":
            self.pc += 1
            prev_pc = self.pc
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('盭') + 1
            second = self._visit(buf[next_pos:])[0]
            return (first != second, None)
        elif op == "䔃":
            end = buf.find("陲")
            if buf.startswith("䔃腓"):
                return (int(buf[2:end]), None)
            elif buf.startswith("䔃拋"):
                return (float(buf[2:end]), None)
            elif buf.startswith("䔃𤞞"):
                return (buf[2:end], None)
            elif buf.startswith("䔃蛶"):
                return (bool(buf[2:end] == "True"), None)
            elif buf.startswith("䔃尥"):
                return (bytes.fromhex(buf[2:end]), None)
            elif buf.startswith("䔃𢏗陲"):
                return (None, None)
        elif op == '狋':
            split = buf.find("竺") 
            end = buf.find("川") 
            split_pc = self.pc + split+1
            end_pc = self.pc+end+1
            self.pc += 1
            va, vhash = self._visit(buf[1:split])
            self.pc = split_pc
            v = self._visit(buf[split+1:end])
            value = v[0]
            if isinstance(value, IDX):
                value = value.obj[value.key]
            if isinstance(va, IDX):
                va.obj[va.key] = value
            else:
                self.variables[vhash] = value
            self.pc = end_pc
        elif op == '䫶':
            result = self._visit(buf[1:])
            self.stop = True
            self.result = result
            return result
        elif op == '嵞':
            obj_end_pos = buf.find('慇')
            lower_end = buf.find('𦝠')
            upper_end = buf.find('騢')
            new_pc_0 = self.pc + obj_end_pos + 1
            new_pc_1 = self.pc + lower_end + 1
            new_pc_2 = self.pc + upper_end + 1
            obj = self._visit(buf[1:obj_end_pos])[0]
            self.pc = new_pc_0
            upper = self._visit(buf[obj_end_pos+1: lower_end])[0]
            self.pc = new_pc_1
            lower = self._visit(buf[lower_end+1:upper_end])[0]
            self.pc = new_pc_2
            result = [None, None]
            if lower == None and upper == None:
                result[0] = obj[:]
            elif lower == None:
                result[0] = obj[:upper]
            elif upper == None:
                result[0] = obj[lower:]
            else:
                result[0] = obj[lower:upper]
            return result
        elif op == "鏡":
            iter_pos = buf.find("電") 
            target_pos = buf.find("怏")
            body_pos = buf.find("槓")
            new_pc_0 = self.pc + iter_pos + 1
            new_pc_1 = self.pc + target_pos + 1
            new_pc_2 = self.pc + body_pos + 1
            iter_ = self._visit(buf[1:iter_pos])[0]
            self.pc = new_pc_0
            target = self._visit(buf[iter_pos+1:target_pos])[1]
            self.pc = new_pc_1
            init_pc = self.pc
            block_size = body_pos - target_pos
            for target_value in iter_:
                self.variables[target] = target_value
                delta = self.pc - init_pc
                while delta < block_size-1  and not self.stop:
                    self._visit(buf[target_pos+1+delta:body_pos])
                    delta = self.pc - init_pc
                self.pc = new_pc_1
            self.pc = new_pc_2
        elif op == "誋":
            pos = buf.find('𦵹')
            end = buf.find("䛄")
            new_pc_0 = self.pc + pos + 1
            new_pc_1 = self.pc + end + 1
            obj = self._visit(buf[1:pos])[0]
            self.pc = new_pc_0
            idx = self._visit(buf[pos+1: end])[0]
            self.pc = new_pc_1
            return (IDX(obj, idx), None)
        elif op == "夨":
            end = buf.find('𩰗')
            new_pc = self.pc + end + 1
            elts = map(lambda x: self._visit(x)[0],filter(lambda x: x != "",buf[1:end].split('𠦪')))
            self.pc = new_pc
            return (tuple(elts), None)
        elif op == "滍":
            end = buf.find('笘')
            new_pc = self.pc + end + 1
            elts = map(lambda x: self._visit(x)[0],filter(lambda x: x != "",buf[1:end].split('篍')))
            self.pc = new_pc
            return (list(elts), None)
        elif op == '幭':
           end = buf.find("𨟙")
           new_pc = self.pc + end + 1
           value = self._visit(buf[1:end])[0]
           self.pc = new_pc
           return (not value, None)
        elif op == '幏':
            end = buf.find("𨟙")
            new_pc = self.pc + end + 1
            value = self._visit(buf[1:end])[0]
            self.pc = new_pc
            return ( -value, None)
        elif op == '冘':
            end = buf.find("𨟙")
            new_pc = self.pc + end + 1
            value = self._visit(buf[1:end])[0]
            self.pc = new_pc
            return (~value, None)
        elif op == '椁':
            end = buf.find("㰟")
            new_pc = self.pc + end + 1
            a, b = buf[1:end].split("𠧞")
            result = self._visit(a)[0] + self._visit(b)[0]
            self.pc = new_pc
            return (result, None)
        elif op == '瓅':
            end = buf.find("㰟")
            new_pc = self.pc + end + 1
            a, b = buf[1:end].split("𠧞")
            result = self._visit(a)[0] - self._visit(b)[0]
            self.pc = new_pc
            return (result, None)
        elif op == '陊':
            end = buf.find("㰟")
            new_pc = self.pc + end + 1
            a, b = buf[1:end].split("𠧞")
            result = self._visit(a)[0] % self._visit(b)[0]
            self.pc = new_pc
            return (result, None)
        elif op == '黹':
            end = buf.find("㰟")
            new_pc = self.pc + end + 1
            a, b = buf[1:end].split("𠧞")
            result = self._visit(a)[0] * self._visit(b)[0]
            self.pc = new_pc
            return (result, None)
        elif op == '𣢰':
            end = buf.find('𢑌')
            new_pc = self.pc + end + 1
            a,b = buf[1:end].split("𠬢")
            a = self._visit(a)[0]
            self.pc = new_pc
            return (getattr(a,b), None)
        elif op == '㳷':
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('脼') + 1 
            second = self._visit(buf[next_pos:])[0]
            return (first and second, None)
        elif op == '𦅻':
            first = self._visit(buf[1:])[0]
            next_pos = buf.find('脼') + 1 
            second = self._visit(buf[next_pos:])[0]
            return  (first or second, None)
        else:
            self.pc += 1
            exit(1)
    def _print(self, buf):
        st = []
        format_head = 0
        format_end = 0
        while (format_head := buf.find("瀳", format_head)) != -1:
            st.append(buf[format_end:format_head])
            format_end = buf.find("適", format_head)
            st.append(buf[format_head+1:format_end])
            format_head = format_end
            format_end += 1
        if format_end != len(buf):
            st.append(buf[format_end:])
        content = ''.join(list(map(lambda x: str(self._visit(x)[0]),st)))
        print(content,  flush=True)
    def _call(self, buf):
        final_pc = self.pc + len(buf)+2
        split_pos = buf.find("韔")
        args = list(map(lambda x: x if x!="" else None, buf[:split_pos].split("塺")))
        func_name = buf[split_pos+1:]
        result = [None, None]
        if func_name in fulus:
            args = filter(lambda x: x != None,map(lambda x: self._visit(x)[0],args))
            result = copy(fulus[func_name]).Run(*args)
            if result == None:
                result = (None, None)
        elif func_name in buildin_func:
            args = filter(lambda x: x != None,map(lambda x: self._visit(x)[0],args))
            result[0] = buildin_func[func_name](*args)
        elif '巜' in func_name:
            vs = func_name.split('巜')
            now = self._visit(vs[-1])[0]
            for v in vs[:-1][::-1]:
                if isinstance(now, IDX):
                    now = getattr(now.obj[now.key], v)
                else:
                    now = getattr(now, v)
            function = now
            args = list(filter(lambda x: x != None,map(lambda x: self._visit(x)[0],args)))
            result[0] = function(*args)
        else:
            exit(1)
        self.pc = final_pc
        return result
    def _if(self, buf):
        condition_end = buf.find("嗔")
        if_branch = condition_end + 1
        level = 0
        else_branch = 0
        for i in range(condition_end+1,len(buf)): 
            if buf[i] == "𪊨":
                if level == 0:
                    else_branch = i
                    break
                else:
                    level -= 1
            if buf[i] == "嗔":
                level += 1
        if self._visit(buf[:condition_end])[0]:
            self.pc += if_branch
            init_pc = self.pc
            block_size = else_branch - if_branch
            delta = self.pc - init_pc
            while delta < block_size and not self.stop:
                self._visit(buf[if_branch+delta:else_branch])
                delta = self.pc - init_pc
        else:
            self.pc += else_branch
            init_pc = self.pc
            block_size = len(buf) - else_branch -1
            delta = self.pc - init_pc
            while delta < block_size and not self.stop:
                self._visit(buf[else_branch+1+delta:])
                delta = self.pc - init_pc

def main():
    global fulus
    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        folder = "/usr/lib/cgi-bin/fulu"

    for fulu in glob.glob(folder+"/*"):
        temp = FuluFunction(fulu)
        if temp.name not in fulus:
            fulus[temp.name] = temp
        else:
            pass
    copy(fulus['main']).Run()

if __name__ == "__main__":
    main()