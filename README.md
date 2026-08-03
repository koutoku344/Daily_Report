# Terraformメモ

---

## 1. 前提

* AWS構成
  * VPC
  * ALB
  * EC2
  * RDS

* Terraform構成
  *  `envs/dev` / `envs/prod` が環境ごとのルートモジュール
  * `modules/*` が再利用用の子モジュール

---

## 2. ディレクトリ構成

```text
terraform/
├── README.md
├── versions.tf
├── providers.tf
├── backend.tf
├── locals.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── outputs.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── outputs.tf
└── modules/
    ├── vpc/
    │   ├── main.tf
    │   ├── variables.tf
    │   ├── outputs.tf
    │   └── versions.tf
    ├── alb/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── ec2/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── rds/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

---

## 3. 役割
各ファイルの役割は次の通りである。
| ファイル | 役割 |
| ---- | ---- |
| envs/dev/main.tf | 開発環境で使う module 呼び出す |
| envs/dev/variables.tf | 開発環境専用の変数定義  |
| envs/dev/terraform.tfvars  | 変数の値を定義 |
| envs/dev/outputs.tf | Terraform apply（またはoutput）を実行したときに出力する値を定義。人が確認したり他moduleに渡される際に利用  |
| modules/vpc/main.tf  | VPC、Subnet、Route Table、IGW、NAT Gateway などを作成  |
| modules/vpc/variables.tf  | VPC CIDR、Subnet CIDR などの入力値を定義 |
| modules/vpc/  | Terraform apply（またはoutput）を実行したときに出力する値を定義。人が確認したり他moduleに渡される際に利用  |

---

4. Terraformでよく出る3種類
4.1 入力変数
外から受け取る値
var.xxx で参照する
hcl


variable "vpc_cidr" {
  type = string
}
hcl


var.vpc_cidr
4.2 リソース
Terraformが作るAWSリソース
hcl


resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr
}
aws_vpc.this がリソース参照
4.3 リソース属性
作成したリソースが持つ値
hcl


aws_vpc.this.id
aws_vpc.this.cidr_block
aws_vpc.this.cidr_block
自分で設定した値
aws_vpc.this.id
AWSが返す値
5. 左辺と右辺の意味
5.1 親モジュール側
hcl


module "vpc" {
  source   = "../../modules/vpc"
  vpc_cidr = var.vpc_cidr
}
左辺 vpc_cidr
子モジュールが受け取る入力名
右辺 var.vpc_cidr
親モジュール側の値
5.2 子モジュール側
hcl


variable "vpc_cidr" {
  type = string
}
hcl


resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr
}
子モジュールでは var.vpc_cidr として使う
cidr_block = vpc_cidr ではない
Terraformの入力変数は常に var. を付ける
6. 名前を変えてもよいか
6.1 可能
親側:

hcl


module "vpc" {
  source    = "../../modules/vpc"
  vpc_cidrA = var.vpc_cidr
}
子側:

hcl


variable "vpc_cidrA" {
  type = string
}
hcl


resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidrA
}
6.2 注意点
親の左辺
子の variable 名
この2つは一致が必要

6.3 実務上
同じ名前にそろえる方が分かりやすい
7. var. が付くもの / 付かないもの
7.1 var. が付くもの
入力変数
hcl


var.name
var.vpc_cidr
var.db_name
7.2 var. が付かないもの
リソース
リソース属性
module出力
hcl


aws_vpc.this.id
aws_vpc.this.cidr_block
module.vpc.vpc_id
8. aws_vpc.this.id の意味
8.1 これは何か
aws_vpc.this で作成したVPCのID
dev側から渡された変数ではない
8.2 箱はどこか
variable で定義するものではない
resource "aws_vpc" "this" を定義すると
Terraform / AWS Provider が内部的に保持する
8.3 つまり
var.xxx は自分で定義する箱
aws_vpc.this.id はresourceを作ると自動で持てる属性
9. aws_vpc.this.cidr_block の値はどこで入るか
hcl


resource "aws_vpc" "this" {
  cidr_block = var.vpc_cidr
}
左辺 cidr_block
VPCリソースの設定項目
右辺 var.vpc_cidr
子モジュールの入力変数
つまり

hcl


aws_vpc.this.cidr_block
の値はここで設定される

10. 依存関係
text


envs/dev/terraform.tfvars
  ↓
envs/dev/variables.tf
  ↓
envs/dev/main.tf
  ├─ module.vpc  -> modules/vpc
  ├─ module.alb  -> modules/alb
  ├─ module.ec2  -> modules/ec2
  └─ module.rds  -> modules/rds
  ↓
envs/dev/outputs.tf
11. モジュール間の依存関係
text


module.vpc
 ├─ vpc_id
 ├─ public_subnet_ids
 └─ private_subnet_ids
      ↓
module.alb / module.ec2 / module.rds

module.alb
 ├─ target_group_arn
 └─ alb_sg_id
      ↓
module.ec2

module.ec2
 └─ ec2_sg_id
      ↓
module.rds
