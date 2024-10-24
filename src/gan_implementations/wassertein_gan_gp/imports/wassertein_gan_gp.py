import torch
import sys
from torch.utils.data import DataLoader
from torch.autograd import Variable
import argparse
sys.path.append("../../../../")
from src.gan_implementations.imports_gan_skeleton import ImportsGAN
from src.gan_implementations.utils import load_json
from src.gan_implementations.wassertein_gan_gp.imports.generator_network import GeneratorNetwork
from src.gan_implementations.wassertein_gan_gp.imports.critic_network import CriticNetwork
from src.gan_implementations.metrics.frechlet_inception_distance import calculate_fid
from src.gan_implementations.imports_dataset import ImportsDataset
from src.gan_implementations.metrics.euclidean_distance import euclidean_distance_np
import torch.autograd as autograd
import os
import numpy as np
import wandb
from scipy.spatial.distance import pdist
os.environ["WANDB_API_KEY"] = "29497eb1bf4e1c185191f4f37528c43459adeb6e"
os.environ["WANDB_MODE"] = "offline"
wandb.login(key=os.environ['WANDB_API_KEY'])
class WasserteinImportsGradientPenaltyGAN(ImportsGAN):
    def compute_gradient_penalty(self, D, real_samples, fake_samples):
        """Calculates the gradient penalty loss for WGAN GP"""
        # Random weight term for interpolation between real and fake samples
        alpha = self.Tensor(np.random.random((real_samples.size(0), 1,)))
        # Get random interpolation between real and fake samples
        interpolates = (alpha * real_samples + ((1 - alpha) * fake_samples)).requires_grad_(True)
        d_interpolates = D(interpolates)
        fake = Variable(self.Tensor(real_samples.shape[0], 1).fill_(1.0), requires_grad=False)
        # Get gradient w.r.t. interpolates
        gradients = autograd.grad(
            outputs=d_interpolates,
            inputs=interpolates,
            grad_outputs=fake,
            create_graph=True,
            retain_graph=True,
            only_inputs=True,
        )[0]
        gradients = gradients.view(gradients.size(0), -1)
        gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean()
        return gradient_penalty

    def initialize_optimizers(self, training_parameters:dict):
        optimizer_G = torch.optim.Adam(self.generator.parameters(), lr=training_parameters["lr"]["generator"],
                                       betas=(training_parameters["beta1"], training_parameters["beta2"]))
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=training_parameters["lr"]["discriminator"],
                                       betas=(training_parameters["beta1"], training_parameters["beta2"]))
        optimizers = {"G": optimizer_G,
                      "D": optimizer_D}
        return optimizers

    def initialize_criterions(self):
        return None

    def build_generator_network(self, generator_parameters_filepath :str):
        self.generator_parameters = load_json(generator_parameters_filepath)
        self.generator = GeneratorNetwork(self.generator_parameters)
        self.generator.to(self.device)

    def build_discriminator_network(self, discriminator_parameters_filepath :str):
        self.discriminator_parameters = load_json(discriminator_parameters_filepath)
        self.discriminator = CriticNetwork(self.discriminator_parameters)
        self.discriminator.to(self.device)


    def run_training_epoch(self, criterions:dict, optimizers:dict, info:dict, training_parameters:dict, epoch:int):


        print("Epoch: {}".format(epoch))
        self.logger.info("\nEpoch: {}".format(epoch))

        # Freeze the generator and train the discriminator


        discriminator_dataloader = DataLoader(
            self.training_discriminator_dataset,
            batch_size=training_parameters["batch_size"],
            shuffle=True,
            drop_last=True,
            # collate_fn=custom_collate_fn
        )
        generator_dataloader = DataLoader(
            self.training_generator_dataset,
            batch_size=training_parameters["batch_size"],
            shuffle=True,
            drop_last=True,
            # collate_fn=custom_collate_fn
        )
        generator_iterator = iter(generator_dataloader)
        discriminator_iterator = iter(discriminator_dataloader)

        valid_labels = Variable(self.Tensor(training_parameters["batch_size"]).fill_(-1.0), requires_grad=False).to(
            self.device)
        fake_labels = Variable(self.Tensor(training_parameters["batch_size"]).fill_(1.0), requires_grad=False).to(
            self.device)
        
        i = 1
        try:
            while True:
                # 获取下一个批次


                d_features, d_hashed_features, d_paths, d_ember_features_v1, d_ember_features_v2, d_raw_paths, d_y = next(discriminator_iterator)
                g_features, g_hashed_features, g_paths, g_ember_features_v1, g_ember_features_v2, g_raw_paths, g_y = next(
                    generator_iterator)

                ############################
                # (1) Update D network
                ###########################
                # Train with all real-batch
                optimizers["D"].zero_grad()
                d_features = d_features.to(self.device)  # Move to GPU if available
                d_output_real = self.discriminator(d_features).view(-1)
                D_x = d_output_real.mean().item()

                g_features = g_features.to(self.device)  # Move to GPU if available
                noise = torch.randn(training_parameters["batch_size"], self.generator_parameters["z_size"]).to(
                    self.device)
                fake_samples = self.generator([g_features, noise])

                # Classify all fake batch with D
                d_output_fake = self.discriminator(fake_samples.detach()).view(-1)
                D_G_z1 = d_output_fake.mean().item()

                # Calculate D's loss
                gradient_penalty = self.compute_gradient_penalty(self.discriminator, d_features.data, fake_samples.data)
                errD = -torch.mean(d_output_real) + torch.mean(d_output_fake) + training_parameters[
                    "lambda_gp"] * gradient_penalty
                errD.backward()
                optimizers["D"].step()
                info["losses"]["train"]["D"].append(errD.item())

                if self.is_wandb == True:
                    wandb.log(
                        {
                            "Training D loss": errD.item()
                        },
                    )

                if i % training_parameters["n_critic"] == 0:
                    optimizers["G"].zero_grad()  # Generator Parameter Gradient Zero
                    fake_samples = self.generator([g_features, noise])
                    d_output_fake = self.discriminator(fake_samples).view(-1)

                    # Calculate G's loss based on this output
                    errG = -torch.mean(d_output_fake)
                    D_G_z2 = d_output_fake.mean().item()

                    # Calculate gradients for G
                    errG.backward()
                    # Update G
                    optimizers["G"].step()  # Generator Parameter Update

                    print('[%d/%d][%d/%d]\tLoss_D: %.4f\tLoss_G: %.4f\tD_x:%.6f\tD_G_z1:%.6f/D_G_z2:%.6f'
                          % (epoch, training_parameters["num_epochs"], i, len(discriminator_dataloader),
                             errD.item(), errG.item(), D_x, D_G_z1, D_G_z2))
                    info["losses"]["train"]["G"].append(errG.item())
                    if self.is_wandb == True:
                        wandb.log(
                            {
                                "Training G loss": errG.item()
                            },
                        )

                # Output training stats
                if i % training_parameters["log_interval"] == 0:
                    print('[%d/%d][%d/%d]\tLoss_D: %.4f\tLoss_G: %.4f'
                          % (epoch, training_parameters["num_epochs"], i, len(discriminator_dataloader),
                             errD.item(), errG.item()))
                    self.logger.info(
                        '[%d/%d][%d/%d]\tLoss_D: %.4f\tLoss_G: %.4f'
                        % (epoch, training_parameters["num_epochs"], i, len(discriminator_dataloader),
                           errD.item(), errG.item()))

                    self.logger.info("Benign features: {}".format(d_features))
                    self.logger.info("Malicious features: {}".format(g_features))
                    self.logger.info("Fake features: {}".format(fake_samples))
                    self.logger.info("Benign labels: {}".format(d_output_real))
                    self.logger.info("Fake labels: {}".format(d_output_fake))

                    info = self.log(
                        d_features,
                        fake_samples,
                        g_features,
                        g_hashed_features,
                        g_paths,
                        g_ember_features_v1,
                        g_ember_features_v2,
                        g_raw_paths,
                        training_parameters["batch_size"],
                        info
                    )


                if i % training_parameters["eval_interval"] == 0:
                    # Evaluate on a subset of the validation data
                    G_val_loss, D_val_loss, evasion_rates, evaluation_info = self.evaluate(
                        epoch,
                        i,
                        criterions,
                        training_parameters
                    )

                    # Add FID scores and imported functions and collisions
                    info["fid"]["scores"].append(evaluation_info["fid"])
                    info["imported_functions"]["original"].append(
                        sum(evaluation_info["imported_functions"]["original"]) / len(
                            evaluation_info["imported_functions"]["original"]))
                    info["imported_functions"]["fake"].append(sum(evaluation_info["imported_functions"]["fake"]) / len(
                        evaluation_info["imported_functions"]["fake"]))
                    info["collisions"].append(sum(evaluation_info["collisions"]) / len(evaluation_info["collisions"]))

                    # Add distance metrics
                    for metric in evaluation_info["distance_metrics"]:
                        if metric == "euclidean":
                            info["distance_metrics"]["validation"][metric]["between_original_and_fake"].append(
                                sum(evaluation_info["distance_metrics"][metric]["between_original_and_fake"]) / len(
                                    evaluation_info["distance_metrics"][metric]["between_original_and_fake"]))
                            info["distance_metrics"]["validation"][metric]["between_fake"].append(
                                sum(evaluation_info["distance_metrics"][metric]["between_fake"]) / len(
                                    evaluation_info["distance_metrics"][metric]["between_fake"]))

                    if G_val_loss < info["losses"]["best"]["G"]:
                        info["losses"]["best"]["G"] = G_val_loss
                        torch.save(self.generator,
                                   os.path.join(self.output_filepath, "generator/generator_best.pt"))
                    if D_val_loss < info["losses"]["best"]["D"]:
                        info["losses"]["best"]["D"] = D_val_loss
                        torch.save(self.discriminator, os.path.join(self.output_filepath,
                                                                    "discriminator/discriminator_best.pt"))
                    if evaluation_info["fid"] < info["fid"]["best"]:
                        info["fid"]["best"] = evaluation_info["fid"]
                        torch.save(self.generator,
                                   os.path.join(self.output_filepath, "generator/generator_best_fid.pt"))
                        torch.save(self.discriminator, os.path.join(self.output_filepath,
                                                                    "discriminator/discriminator_best_fid.pt"))
                    info = self.save_models(info, evasion_rates)
                i += 1
        except StopIteration:
            pass
        return optimizers, info


    def evaluate(self, epoch:int, i:int, criterions:dict, training_parameters:dict):
        discriminator_dataloader = DataLoader(
            self.validation_discriminator_dataset,
            batch_size=training_parameters["validation_batch_size"],
            shuffle=True,
            drop_last=True,
        )
        generator_dataloader = DataLoader(
            self.validation_generator_dataset,
            batch_size=training_parameters["validation_batch_size"],
            shuffle=True,
            drop_last=True
        )
        generator_iterator = iter(generator_dataloader)
        discriminator_iterator = iter(discriminator_dataloader)

        self.generator.eval()
        self.discriminator.eval()

        evaluation_info = self.initialize_evaluation_info_dictionary()

        G_val_losses = []
        D_val_losses = []

        j = 0

        total_samples = len(self.validation_discriminator_dataset)

        fake_features_list = []
        original_features_list = []

        try:
            while True:
                d_features, d_hashed_features, d_paths, d_ember_features_v1, d_ember_features_v2, d_raw_paths, d_y = next(discriminator_iterator)
                g_features, g_hashed_features, g_paths, g_ember_features_v1, g_ember_features_v2, g_raw_paths, g_y = next(
                    generator_iterator)
                # Benign samples
                d_features = d_features.to(self.device)
                d_output_real = self.discriminator(d_features.detach()).view(-1)

                # Malicious samples
                # Sample a random batch of malware samples
                g_features = g_features.to(self.device)  # Move to GPU if available
                noise = torch.randn(training_parameters["validation_batch_size"], self.generator_parameters["z_size"]).to(
                    self.device)
                fake_samples = self.generator([g_features, noise])

                # Classify all fake batch with D
                d_output_fake = self.discriminator(fake_samples.detach()).view(-1)
                # Calculate D's loss on the all-fake batch
                errD = -torch.mean(d_output_real) + torch.mean(d_output_fake)
                errG = -torch.mean(d_output_fake)

                G_val_losses.append(errG.item())
                D_val_losses.append(errD.item())

                # Store intermediate features from both benign and fake samples
                act2 = self.inception_model.retrieve_features(d_hashed_features)
                act2 = act2.cpu().detach().numpy()
                evaluation_info["intermediate_features"]["benign"].append(act2)

                original_features_list.append(g_features.cpu().detach().numpy())
                fake_features_list.append(fake_samples.cpu().detach().numpy())

                evaluation_info = self.evaluate_against_ml_models(
                    evaluation_info,
                    fake_samples,
                    g_features,
                    g_hashed_features,
                    g_ember_features_v1,
                    g_ember_features_v2,
                    g_paths,
                    g_raw_paths,
                    replace=True
                )
                j += 1
        except StopIteration:
            pass
        original_features_arr = np.array(original_features_list)
        print("Original features array: ", original_features_arr.shape)
        original_features_arr = np.squeeze(original_features_arr)
        print("Original squeezed features array: ", original_features_arr.shape)

        fake_features_arr = np.array(fake_features_list)
        print("Fake features array: ", fake_features_arr.shape)
        fake_features_arr = np.squeeze(fake_features_arr)
        print("Fake squeezed features array: ", fake_features_arr.shape)

        evaluation_info["distance_metrics"]["euclidean"]["between_original_and_fake"].append(
            euclidean_distance_np(original_features_arr, fake_features_arr))
        evaluation_info["distance_metrics"]["euclidean"]["between_fake"].append(
            pdist(fake_features_arr, metric="euclidean"))
        fid_score = calculate_fid(np.concatenate(evaluation_info["intermediate_features"]["fake"]),
                                  np.concatenate(evaluation_info["intermediate_features"]["benign"]))
        evaluation_info["fid"] = fid_score
        print(
            "Epoch: {}; Training Step: {}; Validation set\n Generator error: {}\n Discriminator error: {}".format(epoch,
                                                                                                                  i,
                                                                                                                  sum(
                                                                                                                      G_val_losses) / len(
                                                                                                                      G_val_losses),
                                                                                                                  sum(
                                                                                                                      D_val_losses) / len(
                                                                                                                      D_val_losses)))
        self.logger.info(
            "Epoch: {}; Training Step: {}; Validation set\n Generator error: {}\n Discriminator error: {}".format(epoch,
                                                                                                                  i,
                                                                                                                  sum(
                                                                                                                      G_val_losses) / len(
                                                                                                                      G_val_losses),
                                                                                                                  sum(
                                                                                                                      D_val_losses) / len(
                                                                                                                      D_val_losses)))
        self.print_info(evaluation_info, total_samples)
        self.log_info(evaluation_info, total_samples)
        self.log_to_wandb(evaluation_info, total_samples, "Evaluation")

        output_filepath = os.path.join(self.output_filepath,
                                       "validation_results/validation_{}epoch_{}step.txt".format(epoch, i))
        self.write_to_file(evaluation_info, output_filepath, total_samples)

        self.generator.train()
        self.discriminator.train()

        evasion_rates = {
            "hashed_model_2017": evaluation_info["detections"]["fake"][
                                     "hashed_model_2017"] / total_samples if self.features_model_2017 else 1.0,
            "hashed_model_2018": evaluation_info["detections"]["fake"][
                                     "hashed_model_2018"] / total_samples if self.features_model_2018 else 1.0,
            "ember_model_2017": evaluation_info["detections"]["fake"][
                                    "ember_model_2017"] / total_samples if self.ember_model_2017 else 1.0,
            "ember_model_2018": evaluation_info["detections"]["fake"][
                                    "hashed_model_2018"] / total_samples if self.ember_model_2018 else 1.0,
            "sorel20m_lightgbm_model": evaluation_info["detections"]["fake"][
                                           "sorel20m_lightgbm_model"] / total_samples if self.sorel20m_lightgbm_model else 1.0,
            "sorel20m_ffnn_model": evaluation_info["detections"]["fake"][
                                       "sorel20m_ffnn_model"] / total_samples if self.sorel20m_ffnn_model else 1.0,
            "malconv_model": evaluation_info["detections"]["fake"][
                                 "malconv_model"] / total_samples if self.malconv_model else 1.0,
            "nonnegative_malconv_model": evaluation_info["detections"]["fake"][
                                             "nonneg_malconv_model"] / total_samples if self.malconv_model else 1.0
        }

        return sum(G_val_losses) / len(G_val_losses), sum(D_val_losses) / len(
            D_val_losses), evasion_rates, evaluation_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GAN training')
    """恶意软件"""
    parser.add_argument("--malware_imports_features_filepath",
                        type=str,
                        help="Filepath to maliciouss import features",
                        default="../../../../npz/BODMAS/imports_features/baseline/malicious/")# ../../../../npz/BODMAS/imports_features/baseline/malicious/
    parser.add_argument("--malware_hashed_imports_features_filepath",
                        type=str,
                        help="Filepath to malicious hashed import features",
                        default="../../../../npz/BODMAS/hashed_imports_features/malicious")
    parser.add_argument("--malware_imports_filepath",
                        type=str,
                        help="Filepath to maliciouss import dictionaries",
                        default="../../../../npz/BODMAS/imports/malicious/")
    parser.add_argument("--malware_ember_features_filepath_version1",
                        type=str,
                        help="Filepath to malicious EMBER features (Version 1)",
                        default="../../../../npz/BODMAS/ember_features/2017/malicious/")
    parser.add_argument("--malware_ember_features_filepath_version2",
                        type=str,
                        help="Filepath to malicious EMBER features (Version 2)",
                        default="../../../../npz/BODMAS/ember_features/2018/malicious/")
    parser.add_argument("--malware_raw_executables_filepath",
                        type=str,
                        help="Filepath to goodware raw executables",
                        default="../../../../npz/BODMAS/raw/malicious/")
    """训练，测试和验证注释"""
    parser.add_argument("--training_malware_annotations_filepath",
                        type=str,
                        help="Filepath to malicious annotations (training)",
                        default="../../../../src/annotations/all_features/data/BODMAS_malicious_train_None.csv")
    parser.add_argument("--validation_malware_annotations_filepath",
                        type=str,
                        help="Filepath to malicious annotations (validation)",
                        default="../../../../src/annotations/all_features/data/BODMAS_malicious_validation_None.csv")

    """良性软件"""
    parser.add_argument("--goodware_imports_features_filepath",
                        type=str,
                        help="Filepath to benign import features",
                        default="../../../../npz/BODMAS/imports_features/baseline/benign/")# ../../../../npz/BODMAS/imports_features/baseline/benign/
    parser.add_argument("--goodware_hashed_imports_features_filepath",
                        type=str,
                        help="Filepath to benign hashed import features",
                        default="../../../../npz/BODMAS/hashed_imports_features/benign/")
    parser.add_argument("--goodware_imports_filepath",
                        type=str,
                        help="Filepath to benign import dictionaries",
                        default="../../../../npz/BODMAS/imports/benign")
    parser.add_argument("--goodware_ember_features_filepath_version1",
                        type=str,
                        help="Filepath to goodware EMBER features (Version 1)",
                        default="../../../../npz/BODMAS/ember_features/2017/benign/")
    parser.add_argument("--goodware_ember_features_filepath_version2",
                        type=str,
                        help="Filepath to goodware EMBER features (Version 2)",
                        default="../../../../npz/BODMAS/ember_features/2018/benign/")
    parser.add_argument("--goodware_raw_executables_filepath",
                        type=str,
                        help="Filepath to goodware raw executables",
                        default="../../../../npz/BODMAS/raw/benign/")
    """训练，测试和验证注释"""
    parser.add_argument("--training_goodware_annotations_filepath",
                        type=str,
                        help="Filepath to benign annotations (training)",
                        default="../../../../src/annotations/all_features/data/BODMAS_benign_train_None.csv")
    parser.add_argument("--validation_goodware_annotations_filepath",
                        type=str,
                        help="Filepath to benign annotations (validation)",
                        default="../../../../src/annotations/all_features/data/BODMAS_benign_validation_None.csv")

    parser.add_argument("--vocabulary_mapping_filepath",
                        type=str,
                        help="Vocabulary mapping filepath",
                        default="../../../../src/feature_extractors/imports_vocabulary/baseline/vocabulary/vocabulary_mapping_test.json")# ember/vocabulary/vocabulary_mapping_top150.json
    parser.add_argument("--inverse_vocabulary_mapping_filepath",
                        type=str,
                        help="Inverse vocabulary mapping filepath",
                        default="../../../../src/feature_extractors/imports_vocabulary/baseline/vocabulary/inverse_vocabulary_mapping_test.json")# ember/vocabulary/inverse_vocabulary_mapping_top150.json
    """输出路径"""
    parser.add_argument("--output_filepath",
                        type=str,
                        help="Generator and discriminator torch models filepaths",
                        default="models/MalGAN_top150_import_features/")
    """参数"""
    parser.add_argument("--generator_parameters_filepath",
                        type=str,
                        help="Filepath of the generator parameters",
                        default="hyperparameters/generator_network/baseline_parameters.json")
    parser.add_argument("--discriminator_parameters_filepath",
                        type=str,
                        help="Filepath of the discriminator parameters",
                        default="hyperparameters/discriminator_network/baseline_parameters.json")
    parser.add_argument("--training_parameters_filepath",
                        type=str,
                        help="Training parameters filepath",
                        default="training_parameters/training_parameters.json")
    """测试集注释"""
    parser.add_argument("--test_malware_annotations_filepath",
                        type=str,
                        help="Filepath to malware annotations (test)",
                        default="../../../annotations/all_features/data/BODMAS_malicious_test_None.csv")

    parser.add_argument("--test_goodware_annotations_filepath",
                        type=str,
                        help="Filepath to benign annotations (test)",
                        default="../../../annotations/imports/data/BODMAS_benign_test_None.csv")

    parser.add_argument("--feature_version",
                        type=int,
                        help="EMBER feature version",
                        default=2)# 2

    """机器学习参数"""
    parser.add_argument("--imports_lightgbm_model_filepath_version1",
                        type=str,
                        help="Imports black-box detector (Version 1)",
                        default="../../../ml_models/lightgbm_models/imports_detector/top150_imports_model_2017.txt")
    parser.add_argument("--imports_lightgbm_model_filepath_version2",
                        type=str,
                        help="Imports black-box detector (Version 2)",
                        default="../../../ml_models/lightgbm_models/imports_detector/top150_imports_model_2018.txt")
    parser.add_argument('--imports-version1', dest='imports_version1', action='store_true')
    parser.add_argument('--no-imports-version1', dest='imports_version1', action='store_false')
    parser.set_defaults(imports_version1=False)
    parser.add_argument('--imports-version2', dest='imports_version2', action='store_true')
    parser.add_argument('--no-imports-version2', dest='imports_version2', action='store_false')
    parser.set_defaults(imports_version2=False)

    parser.add_argument("--hashed_imports_lightgbm_model_filepath_version1",
                        type=str,
                        help="Hashed imports black-box detector (Version 1)",
                        default="../../../ml_models/lightgbm_models/hashed_imports_detector/hashed_features_model_2017.txt")
    parser.add_argument("--hashed_imports_lightgbm_model_filepath_version2",
                        type=str,
                        help="Hashed imports black-box detector (Version 2)",
                        default="../../../ml_models/lightgbm_models/hashed_imports_detector/hashed_features_model_2018.txt")
    parser.add_argument('--hashed-version1', dest='hashed_version1', action='store_true')
    parser.add_argument('--no-hashed-version1', dest='hashed_version1', action='store_false')
    parser.set_defaults(hashed_version1=False)
    parser.add_argument('--hashed-version2', dest='hashed_version2', action='store_true')
    parser.add_argument('--no-hashed-version2', dest='hashed_version2', action='store_false')
    parser.set_defaults(hashed_version2=False)

    parser.add_argument("--ember_model_filepath_version1",
                        type=str,
                        help="EMBER 2017 Black-box detector (Version 1)",
                        default="../../../ml_models/lightgbm_models/ember_detector/ember_model_2017.txt")
    parser.add_argument("--ember_model_filepath_version2",
                        type=str,
                        help="EMBER 2018 Black-box detector (Version 2)",
                        default="../../../ml_models/lightgbm_models/ember_detector/ember_model_2018.txt")
    parser.add_argument('--ember-version1', dest='ember_version1', action='store_true')
    parser.add_argument('--no-ember-version1', dest='ember_version1', action='store_false')
    parser.set_defaults(ember_version1=False)
    parser.add_argument('--ember-version2', dest='ember_version2', action='store_true')
    parser.add_argument('--no-ember-version2', dest='ember_version2', action='store_false')
    parser.set_defaults(ember_version2=False)

    parser.add_argument("--sorel20m_lightgbm_model_filepath",
                        type=str,
                        help="SOREL-20M lightGBM black-box detector (Version 2)",
                        default="../../../ml_models/lightgbm_models/sorel20m_detector/seed0/lightgbm.model")
    parser.add_argument("--sorel20m_ffnn_model_filepath",
                        type=str,
                        help="SOREL-20M FFNN black-box detector (Version 2)",
                        default="../../../ml_models/torch_models/sorel20m_detector/seed0/epoch_10.pt")
    parser.add_argument('--sorel20m-lightgbm', dest='sorel20m_lightgbm', action='store_true')
    parser.add_argument('--no-sorel20m-lightgbm', dest='sorel20m_lightgbm', action='store_false')
    parser.set_defaults(sorel20m_lightgbm=False)
    parser.add_argument('--sorel20m-ffnn', dest='sorel20m_ffnn', action='store_true')
    parser.add_argument('--no-sorel20m-ffnn', dest='sorel20m_ffnn', action='store_false')
    parser.set_defaults(sorel20m_ffnn=False)

    parser.add_argument("--malconv_model_filepath",
                        type=str,
                        help="MalConv black-box detector (Version 2)",
                        default="../../../ml_models/torch_models/malconv_detector/models/malconv.h5")
    parser.add_argument('--malconv', dest='malconv', action='store_true')
    parser.add_argument('--no-malconv', dest='malconv', action='store_false')
    parser.set_defaults(malconv=False)

    parser.add_argument("--nonneg_malconv_model_filepath",
                        type=str,
                        help="Non-negative MalConv black-box detector (Version 2)",
                        default="../../../ml_models/torch_models/nonnegative_malconv_detector/models/nonneg.checkpoint")
    parser.add_argument('--nonneg-malconv', dest='nonneg_malconv', action='store_true')
    parser.add_argument('--no-nonneg-malconv', dest='nonneg_malconv', action='store_false')
    parser.set_defaults(nonneg_malconv=False)

    parser.add_argument("--malconvgct_model_filepath",
                        type=str,
                        help="MalConvGCT black-box detector (Version 2)",
                        default="../../../ml_models/torch_models/malconvgct_detector/models/malconvGCT_nocat.checkpoint")
    parser.add_argument('--malconvgct', dest='malconvgct', action='store_true')
    parser.add_argument('--no-malconvgct', dest='malconvgct', action='store_false')
    parser.set_defaults(malconvgct=False)

    parser.add_argument("--cuda_device",
                        type=int,
                        help="Cuda device",
                        default=0)
    """inception块"""
    parser.add_argument("--inception_parameters_filepath",
                        type=str,
                        help="Inception parameters",
                        default="../../../ml_models/torch_models/inception_detector/network_parameters/iat_net_params.json")
    parser.add_argument("--inception_checkpoint",
                        type=str,
                        help="Inception checkpoint",
                        default="../../../ml_models/torch_models/inception_detector/models/imports_model_2017/best/best_model.pt")
    parser.add_argument("--inception_features_filepath",
                        type=str,
                        help="Inception benign intermediate features",
                        default="../../../ml_models/torch_models/inception_detector/intermediate_features/imports_2017.npz")

    parser.add_argument('--wandb', dest='wandb', action='store_true')
    parser.add_argument('--no-wandb', dest='wandb', action='store_false')
    parser.set_defaults(wandb=False)# True
    args = parser.parse_args()

    gan = WasserteinImportsGradientPenaltyGAN()
    gan.create_logger(args.output_filepath)
    gan.init_directories(args.output_filepath)
    gan.init_cuda(args.cuda_device)
    gan.initialize_vocabulary_mapping(args.vocabulary_mapping_filepath)
    gan.initialize_inverse_vocabulary_mapping(args.inverse_vocabulary_mapping_filepath)
    gan.initialize_feature_extractor()
    gan.initialize_ember_feature_extractors()

    gan.initialize_training_and_validation_generator_datasets(
        args.malware_imports_features_filepath,
        args.malware_hashed_imports_features_filepath,
        args.malware_imports_filepath,
        args.malware_ember_features_filepath_version1,
        args.malware_ember_features_filepath_version2,
        args.malware_raw_executables_filepath,
        args.training_malware_annotations_filepath,
        args.validation_malware_annotations_filepath
    )
    gan.initialize_training_and_validation_discriminator_datasets(
        args.goodware_imports_features_filepath,
        args.goodware_hashed_imports_features_filepath,
        args.goodware_imports_filepath,
        args.goodware_ember_features_filepath_version1,
        args.goodware_ember_features_filepath_version2,
        args.goodware_raw_executables_filepath,
        args.training_goodware_annotations_filepath,
        args.validation_goodware_annotations_filepath
    )

    gan.build_generator_network(args.generator_parameters_filepath)
    gan.build_discriminator_network(args.discriminator_parameters_filepath)
    gan.build_blackbox_detectors(
        args.imports_lightgbm_model_filepath_version1,
        args.imports_version1,
        args.imports_lightgbm_model_filepath_version2,
        args.imports_version2,
        args.hashed_imports_lightgbm_model_filepath_version1,
        args.hashed_version1,
        args.hashed_imports_lightgbm_model_filepath_version2,
        args.hashed_version2,
        args.ember_model_filepath_version1,
        args.ember_version1,
        args.ember_model_filepath_version2,
        args.ember_version2,
        args.sorel20m_lightgbm_model_filepath,
        args.sorel20m_lightgbm,
        args.sorel20m_ffnn_model_filepath,
        args.sorel20m_ffnn,
        args.malconv_model_filepath,
        args.malconv,
        args.nonneg_malconv_model_filepath,
        args.nonneg_malconv,
        args.malconvgct_model_filepath,
        args.malconvgct
    )
    inception_parameters = load_json(args.inception_parameters_filepath)
    gan.load_inception_model(inception_parameters, args.inception_checkpoint)
    gan.load_inception_benign_intermediate_features(args.inception_features_filepath)

    training_parameters = load_json(args.training_parameters_filepath)
    gan.init_wandb(training_parameters, args.wandb)
    gan.train(training_parameters)

    if args.test_malware_annotations_filepath is not None and args.test_goodware_annotations_filepath is not None:

        test_generator_dataset = ImportsDataset(
            args.malware_imports_features_filepath,
            args.malware_hashed_imports_features_filepath,
            args.malware_imports_filepath,
            args.malware_ember_features_filepath_version1,
            args.malware_ember_features_filepath_version2,
            args.malware_raw_executables_filepath,
            args.test_malware_annotations_filepath
        )
        gan.test(test_generator_dataset, training_parameters["batch_size"])



